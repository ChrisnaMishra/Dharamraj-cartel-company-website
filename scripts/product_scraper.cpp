// Dharamraj Cartel — Indigo kitchenware detail synchronizer.
// C++17 only. Reads the existing product manifest and writes the JSON used by index.html.
// Build: g++ -std=c++17 -O2 scripts/product_scraper.cpp -o /tmp/product_scraper $(pkg-config --cflags --libs libcurl)
// Requires nlohmann-json3-dev.
#include <curl/curl.h>
#include <nlohmann/json.hpp>
#include <algorithm>
#include <chrono>
#include <cctype>
#include <fstream>
#include <iostream>
#include <regex>
#include <set>
#include <string>
#include <thread>
#include <vector>

using json = nlohmann::json;
static const std::string BASE = "https://indigometal.com";
static const std::string MANIFEST = "indigo_images/products.json";
static const std::string OUTPUT = "indigo_images/product-details.json";

static size_t write_body(void* p, size_t size, size_t count, void* out) {
    static_cast<std::string*>(out)->append(static_cast<char*>(p), size * count);
    return size * count;
}

static std::string get_url(const std::string& url) {
    std::string body;
    CURL* curl = curl_easy_init();
    if (!curl) return body;
    curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
    curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1L);
    curl_easy_setopt(curl, CURLOPT_USERAGENT, "Mozilla/5.0 (compatible; DharamrajCartelCatalogue/1.0)");
    curl_easy_setopt(curl, CURLOPT_CONNECTTIMEOUT, 15L);
    curl_easy_setopt(curl, CURLOPT_TIMEOUT, 35L);
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_body);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &body);
    curl_easy_setopt(curl, CURLOPT_ACCEPT_ENCODING, "");
    CURLcode rc = curl_easy_perform(curl);
    long status = 0;
    curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &status);
    curl_easy_cleanup(curl);
    if (rc != CURLE_OK || status < 200 || status >= 400) return {};
    return body;
}

static std::string decode_entities(std::string s) {
    const std::vector<std::pair<std::string,std::string>> replacements = {
        {"&amp;","&"},{"&nbsp;"," "},{"&#160;"," "},{"&ndash;","–"},{"&#8211;","–"},
        {"&mdash;","—"},{"&#8212;","—"},{"&rsquo;","’"},{"&#8217;","’"},
        {"&lsquo;","‘"},{"&#8216;","‘"},{"&quot;","\""},{"&#34;","\""},
        {"&#39;","'"},{"&apos;","'"},{"&lt;","<"},{"&gt;",">"},{"&hellip;","…"}
    };
    for (const auto& r : replacements) {
        size_t pos = 0;
        while ((pos = s.find(r.first, pos)) != std::string::npos) {
            s.replace(pos, r.first.size(), r.second);
            pos += r.second.size();
        }
    }
    return s;
}
static std::string strip_tags(std::string s) {
    s = std::regex_replace(s, std::regex(R"(<script\b[^>]*>[\s\S]*?</script\s*>)", std::regex::icase), " ");
    s = std::regex_replace(s, std::regex(R"(<style\b[^>]*>[\s\S]*?</style\s*>)", std::regex::icase), " ");
    s = std::regex_replace(s, std::regex(R"(<[^>]+>)"), " ");
    s = decode_entities(s);
    s = std::regex_replace(s, std::regex(R"([\t\r\n ]+)"), " ");
    if (!s.empty() && s.front() == ' ') s.erase(0,1);
    if (!s.empty() && s.back() == ' ') s.pop_back();
    return s;
}
static std::string capture(const std::string& html, const std::string& pattern) {
    std::smatch m;
    if (std::regex_search(html, m, std::regex(pattern, std::regex::icase))) return m.size()>1 ? m[1].str() : m[0].str();
    return {};
}
static std::vector<std::string> captures(const std::string& html, const std::string& pattern) {
    std::vector<std::string> out;
    std::regex re(pattern, std::regex::icase);
    for (std::sregex_iterator i(html.begin(), html.end(), re), end; i != end; ++i)
        if (i->size() > 1) out.push_back((*i)[1].str());
    return out;
}
static std::string attr(const std::string& tag, const std::string& name) {
    return capture(tag, name + R"(\s*=\s*["']([^"']+)["'])");
}
static std::string normalize_space(std::string s) {
    s = std::regex_replace(s, std::regex(R"([\t\r\n ]+)"), " ");
    return s;
}
static json scrape(const std::string& url, const json& fallback, const std::string& category) {
    std::string html = get_url(url);
    json images = fallback.value("image_urls", json::array());
    json result = {
        {"name", fallback.value("name", std::string("Kitchenware product"))},
        {"category", category}, {"url", url}, {"description", ""},
        {"specifications", json::array()}, {"features", json::array()},
        {"image_urls", images}, {"supplier_categories", json::array()},
        {"source", "Indigo Metalware LLP"}
    };
    if (html.empty()) {
        result["sync_error"] = "Supplier page could not be fetched; manifest details retained.";
        return result;
    }

    std::string title = strip_tags(capture(html, R"(<h1\b[^>]*>([\s\S]*?)</h1>)"));
    if (title.empty()) title = strip_tags(capture(html, R"(<title\b[^>]*>([\s\S]*?)</title>)"));
    if (!title.empty()) {
        title = std::regex_replace(title, std::regex(R"(\s*[-|]\s*Indigo Metalware LLP.*$)", std::regex::icase), "");
        result["name"] = title;
    }

    std::string description = capture(html, R"(<div[^>]*(?:id=["']tab-description["']|class=["'][^"']*woocommerce-Tabs-panel--description[^"']*["'])[^>]*>([\s\S]*?)(?:</div>\s*</div>|Related products))");
    if (description.empty()) description = capture(html, R"(<div[^>]*class=["'][^"']*woocommerce-product-details__short-description[^"']*["'][^>]*>([\s\S]*?)</div>)");
    if (description.empty()) description = capture(html, R"(<div[^>]*class=["'][^"']*summary[^"']*["'][^>]*>([\s\S]*?)</div>)");
    std::string plain = strip_tags(description);
    plain = std::regex_replace(plain, std::regex(R"((Add to cart|Shopping Basket).*$)", std::regex::icase), "");
    result["description"] = plain.substr(0, 6500);

    std::set<std::string> seenRows;
    std::regex tableRe(R"(<table\b[^>]*>([\s\S]*?)</table>)", std::regex::icase);
    for (std::sregex_iterator ti(html.begin(), html.end(), tableRe), te; ti != te; ++ti) {
        std::string table = (*ti)[1].str();
        for (const auto& tr : captures(table, R"(<tr\b[^>]*>([\s\S]*?)</tr>)")) {
            json row = json::array();
            for (const auto& cell : captures(tr, R"(<t[hd]\b[^>]*>([\s\S]*?)</t[hd]>)")) {
                std::string value = strip_tags(cell);
                if (!value.empty()) row.push_back(value);
            }
            if (row.size() >= 2) {
                std::string key = row.dump();
                if (seenRows.insert(key).second && result["specifications"].size() < 40)
                    result["specifications"].push_back(row);
            }
        }
    }

    std::string featureRoot = description.empty() ? html : description;
    for (const auto& li : captures(featureRoot, R"(<li\b[^>]*>([\s\S]*?)</li>)")) {
        std::string feature = strip_tags(li);
        if (!feature.empty() && feature.size() < 260 && result["features"].size() < 20)
            result["features"].push_back(feature);
    }
    if (result["features"].empty()) {
        for (const auto& p : captures(featureRoot, R"(<p\b[^>]*>([\s\S]*?)</p>)")) {
            std::string feature = strip_tags(p);
            if (!feature.empty() && feature.size() < 260 && feature != title)
                result["features"].push_back(feature);
            if (result["features"].size() >= 8) break;
        }
    }

    std::set<std::string> seenImages;
    for (const auto& item : images) if (item.is_string()) seenImages.insert(item.get<std::string>());
    for (const auto& tag : captures(html, R"(<img\b[^>]*>)")) {
        std::string image = attr(tag, "data-large_image");
        if (image.empty()) image = attr(tag, "data-src");
        if (image.empty()) image = attr(tag, "src");
        if (image.rfind("http", 0) == 0 && seenImages.insert(image).second && images.size() < 12)
            images.push_back(image);
    }
    result["image_urls"] = images;

    for (const auto& a : captures(html, R"(<a\b[^>]*class=["'][^"']*(?:posted_in|tagged_as)[^"']*["'][^>]*>([\s\S]*?)</a>)")) {
        std::string value = strip_tags(a);
        if (!value.empty()) result["supplier_categories"].push_back(value);
    }
    return result;
}

int main() {
    curl_global_init(CURL_GLOBAL_DEFAULT);
    std::ifstream input(MANIFEST);
    if (!input) { std::cerr << "Cannot open " << MANIFEST << "\n"; curl_global_cleanup(); return 2; }
    json manifest;
    try { input >> manifest; } catch (const std::exception& e) {
        std::cerr << "Invalid product manifest: " << e.what() << "\n"; curl_global_cleanup(); return 2;
    }
    json products = json::object();
    size_t total = 0, failed = 0;
    for (const auto& group : manifest.value("categories", json::array())) {
        std::string category = group.value("name", std::string("Kitchenware"));
        for (const auto& item : group.value("products", json::array())) {
            std::string url = item.value("url", std::string());
            if (url.empty()) continue;
            ++total;
            json product = scrape(url, item, category);
            if (product.contains("sync_error")) ++failed;
            std::cout << "[" << total << "] " << (product.value("name", std::string("Product"))) << "\n";
            products[url] = std::move(product);
            std::this_thread::sleep_for(std::chrono::milliseconds(180));
        }
    }
    json output = {
        {"source", manifest.value("source", BASE + "/household/")},
        {"generated_at", std::time(nullptr)},
        {"product_count", total}, {"failed_count", failed},
        {"products", products}
    };
    std::ofstream out(OUTPUT);
    if (!out) { std::cerr << "Cannot write " << OUTPUT << "\n"; curl_global_cleanup(); return 3; }
    out << output.dump(2) << "\n";
    std::cout << "Wrote " << total << " product records; " << failed << " pages used manifest fallback.\n";
    curl_global_cleanup();
    return 0;
}
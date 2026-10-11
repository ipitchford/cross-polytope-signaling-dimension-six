#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <limits>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <vector>

namespace {

long long choose(int n, int k) {
    if (k < 0 || k > n) return 0;
    if (k > n - k) k = n - k;
    long long value = 1;
    for (int i = 1; i <= k; ++i) value = value * (n - k + i) / i;
    return value;
}

long long expected_labelled_supports(int k) {
    long long total = 0;
    for (int omitted_rows = 0; omitted_rows <= 6; ++omitted_rows) {
        int available = (1 << (6 - omitted_rows)) - 1;
        long long term = choose(6, omitted_rows) * choose(available, k);
        total += omitted_rows % 2 ? -term : term;
    }
    return total;
}

std::vector<int> decode_graph6(const std::string& record, int right_size) {
    const int order = 6 + right_size;
    if (record.empty() || static_cast<int>(record[0]) - 63 != order) {
        throw std::runtime_error("unexpected graph6 order");
    }
    std::vector<int> bits;
    for (std::size_t i = 1; i < record.size(); ++i) {
        int value = static_cast<unsigned char>(record[i]) - 63;
        if (value < 0 || value > 63) throw std::runtime_error("invalid graph6 byte");
        for (int shift = 5; shift >= 0; --shift) bits.push_back((value >> shift) & 1);
    }
    std::vector<int> columns(right_size, 0);
    std::size_t cursor = 0;
    for (int high = 1; high < order; ++high) {
        for (int low = 0; low < high; ++low) {
            if (cursor >= bits.size()) throw std::runtime_error("truncated graph6 payload");
            if (bits[cursor++]) {
                if (!(low < 6 && high >= 6)) throw std::runtime_error("within-colour edge");
                columns[high - 6] |= 1 << low;
            }
        }
    }
    std::set<int> unique(columns.begin(), columns.end());
    if (unique.size() != columns.size() || *unique.begin() == 0) {
        throw std::runtime_error("zero or duplicate column");
    }
    int row_union = 0;
    for (int column : columns) row_union |= column;
    if (row_union != 63) throw std::runtime_error("isolated row");
    return columns;
}

std::vector<std::array<int, 64>> permutation_maps() {
    std::array<int, 6> permutation{0, 1, 2, 3, 4, 5};
    std::vector<std::array<int, 64>> maps;
    do {
        std::array<int, 64> map{};
        for (int column = 0; column < 64; ++column) {
            int transformed = 0;
            for (int source = 0; source < 6; ++source) {
                if (column & (1 << source)) transformed |= 1 << permutation[source];
            }
            map[column] = transformed;
        }
        maps.push_back(map);
    } while (std::next_permutation(permutation.begin(), permutation.end()));
    if (maps.size() != 720) throw std::runtime_error("coordinate permutation count");
    return maps;
}

std::uint64_t pack(std::vector<int> columns) {
    std::sort(columns.begin(), columns.end());
    std::uint64_t value = 0;
    for (int column : columns) value = (value << 6) | static_cast<std::uint64_t>(column);
    return value;
}

struct Audit {
    long long records = 0;
    long long distinct_canonical_keys = 0;
    long long orbit_size_sum = 0;
    long long expected_labelled = 0;
};

Audit audit_file(const std::string& filename, int right_size,
                 const std::vector<std::array<int, 64>>& maps) {
    std::ifstream input(filename);
    if (!input) throw std::runtime_error("cannot open graph6 file");
    std::unordered_set<std::uint64_t> canonical_keys;
    long long orbit_sum = 0;
    long long records = 0;
    std::string line;
    while (std::getline(input, line)) {
        if (line.empty() || line.rfind(">>", 0) == 0) continue;
        std::vector<int> columns = decode_graph6(line, right_size);
        std::uint64_t canonical = std::numeric_limits<std::uint64_t>::max();
        std::vector<std::uint64_t> orbit;
        orbit.reserve(maps.size());
        for (const auto& map : maps) {
            std::vector<int> transformed;
            transformed.reserve(columns.size());
            for (int column : columns) transformed.push_back(map[column]);
            std::uint64_t code = pack(std::move(transformed));
            canonical = std::min(canonical, code);
            orbit.push_back(code);
        }
        std::sort(orbit.begin(), orbit.end());
        orbit.erase(std::unique(orbit.begin(), orbit.end()), orbit.end());
        if (!canonical_keys.insert(canonical).second) {
            throw std::runtime_error("two graph6 records belong to the same coordinate-permutation orbit");
        }
        orbit_sum += static_cast<long long>(orbit.size());
        ++records;
    }
    long long expected = expected_labelled_supports(right_size);
    if (orbit_sum != expected) throw std::runtime_error("orbit sizes do not cover every labelled support");
    return {records, static_cast<long long>(canonical_keys.size()), orbit_sum, expected};
}

}  // namespace

int main(int argc, char** argv) {
    if (argc != 3) {
        std::cerr << "usage: verify-genbg-orbits GENBG_6_5 GENBG_6_6\n";
        return 2;
    }
    try {
        auto maps = permutation_maps();
        Audit five = audit_file(argv[1], 5, maps);
        Audit six = audit_file(argv[2], 6, maps);
        std::cout << "{\n"
                  << "  \"schema\": \"cross-polytope-six-orbit-audit-v1\",\n"
                  << "  \"coordinate_permutations\": 720,\n"
                  << "  \"right_size_5\": {\"records\": " << five.records
                  << ", \"distinct_canonical_keys\": " << five.distinct_canonical_keys
                  << ", \"orbit_size_sum\": " << five.orbit_size_sum
                  << ", \"expected_labelled_supports\": " << five.expected_labelled << "},\n"
                  << "  \"right_size_6\": {\"records\": " << six.records
                  << ", \"distinct_canonical_keys\": " << six.distinct_canonical_keys
                  << ", \"orbit_size_sum\": " << six.orbit_size_sum
                  << ", \"expected_labelled_supports\": " << six.expected_labelled << "},\n"
                  << "  \"result\": \"all_orbits_unique_and_complete\",\n"
                  << "  \"count_formula\": \"sum_{j=0}^6 (-1)^j binom(6,j) binom(2^(6-j)-1,k)\"\n"
                  << "}\n";
    } catch (const std::exception& error) {
        std::cerr << error.what() << "\n";
        return 1;
    }
    return 0;
}

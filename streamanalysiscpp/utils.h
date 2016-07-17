#ifndef UTILS_H
#define UTILS_H

#include <array>

double getNorm(std::array<double, 2> &euclid);
void polar2euclid(std::array<double, 2> &polar, std::array<double, 2> &euclid);
void euclid2polar(std::array<double, 2> &euclid, std::array<double, 2> &polar);

#endif

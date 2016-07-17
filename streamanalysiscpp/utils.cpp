#include <cmath>
#include <array>
using namespace std;

// Returns the norm of a 2d euclidean array.
double getNorm(array<double, 2> &euclid){
	double n = sqrt(euclid[0] * euclid[0] + euclid[1] * euclid[1]);
	return n;
}

// Converts array in polar coordinates (polar) to euclidean array (euclid).
// Inverse operation of euclid2polar.
void polar2euclid(array<double, 2> &polar, array<double, 2> &euclid){
	euclid[0] = polar[0] * cos(polar[1]);
	euclid[1] = polar[0] * sin(polar[1]);
}

// Converts array in euclidean coordinates (euclid) to polar array (polar).
// Inverse operation of polar2euclid.
void euclid2polar(array<double, 2> &euclid, array<double, 2> &polar){
	polar[0] = getNorm(euclid);
	polar[1] = atan2(euclid[1], euclid[0]);
}


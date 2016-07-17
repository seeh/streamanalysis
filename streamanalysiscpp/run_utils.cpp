#include <iostream>
#include <cmath>
#include "utils.h"
using namespace std;

int main ()
{
	// vector of length 1 and angle pi/4
	array<double, 2> euclid = {1./sqrt(2.0), 1./sqrt(2.0)};
	cout << "Euclidean vector: (" << euclid[0] << ", " << euclid[1] << ")"  << endl;
	double n = getNorm(euclid);
	cout << "Length of vector: " << n << endl;
	array<double, 2> polar;
	euclid2polar(euclid, polar);
	cout << "Vector in polar coordinates: (" << polar[0] << ", " << polar[1] << ")"  << endl;
	array<double, 2> neuclid;
	polar2euclid(polar, neuclid);
	cout << "Transformed back to euclidean coordinates: (" << neuclid[0] << ", " << neuclid[1] << ")"  << endl;
	return 0;
}

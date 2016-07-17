#include <iostream>
#include <fstream>
#include <chrono>
#include <ratio>
#include <array>
#include "athlete.h"
using namespace std;

int main ()
{
	// instantiate athlete
	Athlete ath;
	// get current time
	chrono::system_clock::time_point t = chrono::system_clock::now();
	// get time increments corresponding to 20 Hz
	chrono::duration<long,ratio<1,20>> dt(1);
	// number of measurements corresponding to 90 minutes
	int N = 20 * 60 * 90 + 1;
	// file for saving created data
	ofstream myfile;
	myfile.open ("../notebooks/athlete.out");
	myfile << "Pos-x, Pos-y, Vel-x, Vel-y\n";
	// iterate through N timepoints and store results in myfile
	for (int i = 0; i < N; i++){
		chrono::system_clock::time_point new_time = t + i * dt;
		AthleteSpec as = ath.update(new_time);
		myfile << as.pos[0] << ", ";
		myfile << as.pos[1] << ", ";
		myfile << as.vel[0] << ", ";
		myfile << as.vel[1] << "\n";
	}
	myfile.close();
	return 0;
}

#include <chrono>
#include <vector>
#include <array>
#include "utils.h"
#include "athlete.h"
using namespace std;

const double pi = 3.1415926535897;

// Constructor of Athlete. See Athlete class for default values and attributes.
Athlete::Athlete (array<double, 2> lim, array<double, 2> p0, array<double, 2> v0,
		double maxa, double maxv, double freqa, double deca, bool keep) :
				limits(lim), pos0(p0), vel0(v0), amax(maxa), vmax(maxv), acc_freq(freqa),
				dec_a(deca), keepData(keep) { reset(); }

// Reset athlete to initial position and clear history.
void Athlete::reset(void){
	called = false;
	pos = pos0;
	vel = vel0;
	acc = {0.,0.};
	reset_vel = false;
	reset_acc = false;
	data.clear();
	seed = chrono::system_clock::now().time_since_epoch().count();
	generator.seed(seed);
}

// Manipulates acceleration of athlete and decelerates it by dec_a
void Athlete::decelerate(double dt){
	// Calculate pace of athlete
	double v = getNorm(vel);
	// Decelerate by dec_a if velocity is greater than the amount of deceleration
	if (v > (dec_a * dt)) {
		acc[0] -= (dec_a / v) * vel[0];
		acc[1] -= (dec_a / v) * vel[1];
	}
	// Stop athlete otherwise
	else {
		acc[0] = -vel[0] / dt;
		acc[1] = -vel[1] / dt;
	}
}

// Manipulates acceleration of athlete and draws a random acceleration input
void Athlete::accelerate(double dt){
	// Draw a random acceleration in polar coordinates
	array<double, 2> acc_polar;
	// Draw the magnitude of the acceleration from a linear
	// distribution from 0 to amax
	double r1 = distribution(generator);
	// Draw the angle of the acceleration from a uniform
	// distribution between 0 and 2 pi
	acc_polar[0] = amax * (1 - sqrt(r1));
	double r2 = distribution(generator);
	acc_polar[1] = r2 * (2 * pi);
	// Transform polar acceleration into euclidean coordinates
	polar2euclid(acc_polar, acc);
}

// Update the velocity of the athlete according to acceleration
void Athlete::updateVel(double dt){
	// Naive update according to acc
	vel[0] += acc[0] * dt;
	vel[1] += acc[1] * dt;
	// Make sure velocity is conform with maximum velocity
	// and reset acceleration to zero if vmax is achieved
	double vel_abs = getNorm(vel);
	if (vel_abs > vmax){
		vel[0] *= (vmax/vel_abs);
		vel[1] *= (vmax/vel_abs);
		reset_acc = true;
	}
}

// Update the position of the athlete according to velocity
void Athlete::updatePos(double dt){
	// Copy current position
	array<double,2> oldpos = pos;
	// Naive update according to vel[0]
	pos[0] += vel[0] * dt;
	// Make sure pos[0] is consistent with limits
	// and reset velocity to zero if limits are achieved
	if (pos[0] < 0.0){
		pos[0] = 0.0;
		reset_vel = true;
	}
	if (pos[0] > limits[0]){
		pos[0] = limits[0];
		reset_vel = true;
	}
	// Naive update according to vel[1]
	pos[1] += vel[1] * dt;
	// Make sure pos[1] is consistent with limits
	// and reset velocity to zero if limits are achieved
	if (pos[1] < 0.0){
		pos[1] = 0.0;
		reset_vel = true;
	}
	if (pos[1] > limits[0]){
		pos[1] = limits[0];
		reset_vel = true;
	}
	// If athlete bumped into limits, update the velocity
	// to the value from comparing oldpos to pos and
	// also change direction of acceleration by pi/2
	if (reset_vel) {
		array<double,2> polar_acc;
		euclid2polar(acc, polar_acc);
		polar_acc[1] += (pi * .5);
		polar2euclid(polar_acc, acc);
		vel[0] = (pos[0] - oldpos[0])/dt;
		vel[1] = (pos[1] - oldpos[1])/dt;
	}
}

// Main function of athlete: Takes std::chrono::system_clock::time_point
// and returns updated AthleteSpec. On first call, it returns the initial
// position and velocity.
AthleteSpec Athlete::update(std::chrono::system_clock::time_point time){
	// Set velocity to zero if reset_vel flag is set
	// (happens when athlete bumps into limits)
	if (reset_vel) {
		vel[0] = 0.0;
		vel[1] = 0.0;
		reset_vel = false;
	}
	// Set acceleration to zero if if reset_acc flag is set
	// (happens when athlete achieves maximum velocity)
	if (reset_acc) {
		acc[0] = 0.0;
		acc[1] = 0.0;
		reset_acc = false;
	}
	// Set called to true in initial call to athlete
	if (! called) {
		called = true;
	}
	// Update position and velocity otherwise
	else {
		// Get time-upate in seconds by comparing time to current_time
		chrono::system_clock::duration delta = time - current_time;
		double dt = delta.count();
		dt *= chrono::system_clock::duration::period::num;
		dt /= chrono::system_clock::duration::period::den;
		// Randomly decide to accelerate or decelerate
		double r = distribution(generator);
		if (r > dt * acc_freq){
			decelerate(dt);
		}
		else {
			accelerate(dt);
		}
		updateVel(dt);
		updatePos(dt);
	}
	// set current_time to time
	current_time = time;
	// Create AthleteSpec from pos and vel
	AthleteSpec athlete(pos, vel);
	// Store history if keepData is true
	if (keepData){
		data.push_back(athlete);
	}
	return athlete;
}

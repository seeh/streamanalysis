#ifndef ATHLETE_H
#define ATHLETE_H

#include <random>

// Default values for the limits of the movement, initial position,
// and initial velocity of the athlete.
const std::array<double, 2> defaultLimits = {100.0, 100.0};
const std::array<double, 2> defaultPos0 = {50.0, 50.0};
const std::array<double, 2> defaultVel0 = {0.0, 0.0};

// Struct containing current state of the athlete.
// Contains position array (pos) and velocity array (vel).
struct AthleteSpec {
	std::array<double, 2> pos;
	std::array<double, 2> vel;
	AthleteSpec(std::array<double,2> p, std::array<double,2> v) : pos(p), vel(v) { }
} ;

// Implements an athlete with the following parameters:
// std::array<double, 2> lim : limits of the movement in meters, default: defaultLimits
// std::array<double, 2> p0 : initial position in meters, default: defaultPos0
// std::array<double, 2> v0 : initial veocity in meters/second, default: defaultVel0
// double maxa : maximum acceleration of athlete in meters/second^2, default: 4.0
// double maxv : maximum velocity of athlete in meters/second, default: 9.0
// double freqa : frequency of acceleration input, default: 0.2
// double deca : magnitude of deceleration, default: 0.02
// bool keep : flag for storing the history of the athlete in data vector, default: false
//
// The function update takes a std::chrono::system_clock::time_point and returns
// the updated position and velocity in an AthleteSpec.
class Athlete {
	// Limits of the movement, initial position,
	// and initial velocity of the athlete.
	const std::array<double, 2> limits;
	const std::array<double, 2> pos0;
	const std::array<double, 2> vel0;
	// Maximum acceleration
	const double amax;
	// Maximum velocity
	const double vmax;
	// Frequency of acceleration input
	const double acc_freq;
	// Magnitude of deceleration
	const double dec_a;
	// Flag for keeping data in data vector
	bool keepData;
	// Internal flags
	bool called;
	bool reset_vel;
	bool reset_acc;
	// Random numbers
	std::default_random_engine generator;
	std::uniform_real_distribution<double> distribution{0.0,1.0};
	void decelerate(double dt);
	void accelerate(double dt);
	void updateVel(double dt);
	void updatePos(double dt);
public:
	// Current position, velocity, and acceleration
	std::array<double, 2> pos;
	std::array<double, 2> vel;
	std::array<double, 2> acc;
	// Vector for storing history of athlete in case keepData is true
	std::vector<AthleteSpec> data;
	// Current time of athlete
	std::chrono::system_clock::time_point current_time;
	// seed of athlete
	unsigned seed;
	Athlete (std::array<double, 2> lim = defaultLimits,
			std::array<double, 2> p0 = defaultPos0,
			std::array<double, 2> v0 = defaultVel0,
			double maxa = 4.0, double maxv = 9.0,
			double freqa = .2, double deca = .02, bool keep = false);
	void reset (void);
	AthleteSpec update(std::chrono::system_clock::time_point time);
};

#endif

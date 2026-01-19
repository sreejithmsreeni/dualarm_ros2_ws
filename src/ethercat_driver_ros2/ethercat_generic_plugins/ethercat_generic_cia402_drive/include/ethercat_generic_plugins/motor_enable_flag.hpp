#ifndef MOTOR_ENABLE_FLAG_HPP
#define MOTOR_ENABLE_FLAG_HPP

#include <atomic>

// Global flag accessible from anywhere
inline std::atomic<bool>& getMotorEnableFlag() {
  static std::atomic<bool> flag{false};
  return flag;
}

#endif

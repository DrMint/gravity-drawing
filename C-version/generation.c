#include "TinyPngOut.h"
#include <math.h>
#include <png.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <threads.h>
#include <time.h>

// --[CONFIG]--

static const float RESOLUTION_MULTIPLIER = 1.0f;
static const float SIMULATION_PRECISION_MULTIPLIER = 1.0f;

static const unsigned int NUM_CPU_THREADS = 12;
static const unsigned int NUM_THREADS_PER_CPU_THREADS = 2;

// Calculated
static const unsigned int NUM_THREADS =
    NUM_CPU_THREADS * NUM_THREADS_PER_CPU_THREADS;
static const unsigned int WIDTH = 2160 * RESOLUTION_MULTIPLIER;
static const unsigned int HEIGHT = 3840 * RESOLUTION_MULTIPLIER;
static const unsigned int ITERATION = 200 * SIMULATION_PRECISION_MULTIPLIER;
static const float ITERATION_DURATION =
    20 / SIMULATION_PRECISION_MULTIPLIER * RESOLUTION_MULTIPLIER;
static const float DISTANCE_TRESHOLD = 30 * RESOLUTION_MULTIPLIER;
static const float ITERATION_DURATION_SQUARED =
    ITERATION_DURATION * ITERATION_DURATION;
static const unsigned int ROWS_PER_THREAD = HEIGHT / NUM_THREADS;

// Idea: precalculate a gravity field

typedef struct Color {
  uint8_t r;
  uint8_t g;
  uint8_t b;
} color;

typedef struct Point {
  float x;
  float y;
} point;

typedef struct Attractor {
  float x;
  float y;
  float strength;
  color color;
} attractor;

typedef char *string;

typedef struct ThreadJob {
  thrd_t id;
  unsigned int startingRow;
  unsigned int endingRow;
  color *image;
} threadJob;

static const attractor attractors[3] = {
    {0.31 * WIDTH, 0.36 * HEIGHT, 1, {255, 0, 0}},
    {0.81 * WIDTH, 0.45 * HEIGHT, 1, {0, 0, 255}},
    {0.42 * WIDTH, 0.65 * HEIGHT, 1, {0, 255, 0}}};

void writePng(const string name, const color image[]) {
  FILE *file = fopen(name, "wb");
  struct TinyPngOut pngout;
  TinyPngOut_init(&pngout, WIDTH, HEIGHT, file);
  TinyPngOut_write(&pngout, (uint8_t *)image, WIDTH * HEIGHT);
  fclose(file);
}

color calculateColor(point point) {
  float dx = 0;
  float dy = 0;

  unsigned int i = 0;
  while (i < ITERATION) {
    for (unsigned int i = 0; i < sizeof(attractors) / sizeof(attractor); i++) {
      const attractor attractor = attractors[i];
      const float distanceX = attractor.x - point.x;
      const float distanceY = attractor.y - point.y;
      float distance = sqrtf(powf(distanceX, 2.0f) + powf(distanceY, 2.0f));

      if (distance < DISTANCE_TRESHOLD) {
        return attractor.color;
      }

      const float attractionStrength =
          attractor.strength / powf(distance, 2.0f);
      dx += distanceX * attractionStrength * ITERATION_DURATION_SQUARED;
      dy += distanceY * attractionStrength * ITERATION_DURATION_SQUARED;
    }

    point.x += dx;
    point.y += dy;

    i++;
  }

  return (color){0, 0, 0};
}
int calculateRows(void *argsVoid) {
  threadJob *args = argsVoid;
  for (unsigned int y = args->startingRow; y < args->endingRow; y++) {
    for (unsigned int x = 0; x < WIDTH; x++) {
      const point point = {x, y};
      const int index = WIDTH * point.y + point.x;
      args->image[index] = calculateColor(point);
    }
  }
  return thrd_success;
}

void displayElapsedTime(const struct timespec startingTime,
                        const struct timespec endingTime) {
  double diff = (endingTime.tv_nsec - startingTime.tv_nsec) / 1000000000.0 +
                (endingTime.tv_sec - startingTime.tv_sec);
  printf("Your calculations took %.2lf seconds to run.\n", diff);
}

int main(void) {
  color *image = malloc(WIDTH * HEIGHT * sizeof(color));

  struct timespec startingTime, endingTime;
  threadJob *jobs = malloc(sizeof(threadJob) * NUM_THREADS);

  clock_gettime(CLOCK_MONOTONIC_RAW, &startingTime);
  for (unsigned int t = 0; t < NUM_THREADS; t++) {
    jobs[t].startingRow = t * ROWS_PER_THREAD;
    jobs[t].endingRow = jobs[t].startingRow + ROWS_PER_THREAD;
    jobs[t].image = image;
    thrd_create(&jobs[t].id, calculateRows, &jobs[t]);
  }

  for (unsigned int t = 0; t < NUM_THREADS; t++) {
    thrd_join(jobs[t].id, NULL);
  }
  clock_gettime(CLOCK_MONOTONIC_RAW, &endingTime);
  free(jobs);

  displayElapsedTime(startingTime, endingTime);
  writePng("output.png", image);
  free(image);

  return EXIT_SUCCESS;
}
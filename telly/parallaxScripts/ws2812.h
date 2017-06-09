#ifndef __WS2812_H__
#define __WS2812_H__

#include <stdint.h>

#if defined(__cplusplus)
extern "C" {
#endif

#define TYPE_RGB            0
#define TYPE_GRB            1   // for WS2812 and WS2812B

#define COLOR(r, g, b)      (((r) << 16) | ((g) << 8) | (b))
#define SCALE(x, l)         ((x) * (l) / 255)
#define COLORX(r, g, b, l)  ((SCALE(r, l) << 16) | (SCALE(g, l) << 8) | SCALE(b, l))

//                         RRGGBB
#define COLOR_BLACK      0x000000
#define COLOR_RED        0xFF0000
#define COLOR_GREEN      0x00FF00
#define COLOR_BLUE       0x0000FF
#define COLOR_WHITE      0xFFFFFF
#define COLOR_CYAN       0x00FFFF
#define COLOR_MAGENTA    0xFF00FF
#define COLOR_YELLOW     0xFFFF00
#define COLOR_CHARTREUSE 0x7FFF00
#define COLOR_ORANGE     0xFF6000
#define COLOR_AQUAMARINE 0x7FFFD4
#define COLOR_PINK       0xFF5F5F
#define COLOR_TURQUOISE  0x3FE0C0
#define COLOR_REALWHITE  0xC8FFFF
#define COLOR_INDIGO     0x3F007F
#define COLOR_VIOLET     0xBF7FBF
#define COLOR_MAROON     0x320010
#define COLOR_BROWN      0x0E0600
#define COLOR_CRIMSON    0xDC283C
#define COLOR_PURPLE     0x8C00FF

// driver state structure
typedef struct {
    volatile uint32_t command;
    int cog;
} ws2812_t;

// load a COG with a driver for WS2812 chips
int ws2812_init(ws2812_t *state);

// load a COG with a driver for WS2812B chips (like used in the Parallax WS2812B board)
int ws2812b_init(ws2812_t *state);

// load a COG with a driver using custom parameters
// -- usreset is reset timing (us)
// -- ns0h is 0-bit high timing (ns)
// -- ns0l is 0-bit low timing (ns)
// -- ns1h is 1-bit high timing (ns)
// -- ns1l is 1-bit low timing (ns)
// -- type is TYPE_GRB for ws2812 or ws2812b
int ws_init(ws2812_t *state, int usreset, int ns0h, int ns0l, int ns1h, int ns1l, int type);

// shut down the COG running a driver
void ws2812_close(ws2812_t *statet);

// refresh a chain of LEDs
void ws2812_refresh(ws2812_t *state, int pin, uint32_t *colors, int count);

// create color from a 0 to 255 position input
// -- colors transition r-g-b back to r
uint32_t ws2812_wheel(int pos);

// create color from a 0 to 255 position input
// -- colors transition r-g-b back to r
// -- brightness can be between 0 and 255
uint32_t ws2812_wheel_dim(int pos, int brightness);

#if defined(__cplusplus)
}
#endif

#endif

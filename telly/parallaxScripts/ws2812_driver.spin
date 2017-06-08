'' Modified for use with PropGCC by David Betz
''  Derived from:
''   File....... jm_ws2812.spin
''   Purpose.... 800kHz driver for WS2812 LEDs
''   Author..... Jon "JonnyMac" McPhalen
''               Copyright (c) 2013 Jon McPhalen

{{
    // parameter long
    31:16 base address of array of 32 bit RGB values
    15:8  number of entries in the array
     7:0  pin number
    
    // driver header structure
    typedef struct {
        uint32_t    jmp_inst;
        uint32_t    resettix;
        uint32_t    bit0hi;
        uint32_t    bit0lo;
        uint32_t    bit1hi;
        uint32_t    bit1lo;
        uint32_t    swaprg;
    } ws2812_hdr;
}}

pub driver
  return @ws2812

dat
                        org     0

ws2812                  jmp     #get_cmd

resettix                long    0                               ' frame reset timing
bit0hi                  long    0                               ' bit0 high timing
bit0lo                  long    0                               ' bit0 low timing
bit1hi                  long    0                               ' bit1 high timing    
bit1lo                  long    0                               ' bit1 low timing
swaprg                  long    0                               ' swap r and g     

reset_delay             mov     bittimer, resettix              ' set reset timing  
                        add     bittimer, cnt                   ' sync timer 
                        waitcnt bittimer, #0                    ' let timer expire                             
                        
clear_cmd               mov     t1, #0                          ' clear last command
                        wrlong  t1, par

get_cmd                 rdlong  t1, par                 wz      ' look for packed command
        if_z            jmp     #get_cmd

                        mov     t2, t1                          ' get pin
                        and     t2, #$1F                        ' isolate
                        mov     txmask, #1                      ' create mask for tx
                        shl     txmask, t2
                        andn    outa, txmask                    ' set to output low
                        or      dira, txmask

                        mov     ledcount, t1                    ' get count
                        shr     ledcount, #8                    ' isolate
                        and     ledcount, #$FF                        
                        add     ledcount, #1                    ' update (1 to 256 leds)

                        mov     hubpntr, t1                     ' get hub address
                        shr     hubpntr, #16                    ' isolate
                        
                        mov     addr, hubpntr                   ' point to rgbbuf[0]
                        mov     nleds, ledcount                 ' set # active leds

frame_loop              rdlong  colorbits, addr                 ' read a channel
                        add     addr, #4                        ' point to next

' Correct placement of color bytes for WS2812
'   $RR_GG_BB --> $GG_RR_BB

fix_colors              tjz     swaprg, #shift_out              ' skip if R and G don't need swapping
                        mov     t1, colorbits                   ' copy for red
                        mov     t2, colorbits                   ' copy for green
                        and     colorbits, HX_0000FF            ' isolate blue
                        shr     t1, #8                          ' fix red pos (byte1)
                        and     t1, HX_00FF00                   ' isolate red
                        or      colorbits, t1                   ' add red back in
                        shl     t2, #8                          ' fix green pos (byte2)
                        and     t2, HX_FF0000                   ' isolate green
                        or      colorbits, t2                   ' add green back in

                        
' Shifts long in colorbits to WS2812 chain
'
'  WS2812 Timing 
'
'  0        0.35us / 0.80us
'  1      0.70us / 0.60us
'
'  WS2812B Timing
'
'  0       0.35us / 0.90us
'  1       0.90us / 0.35us
'
'  At least 50us (reset) between frames

shift_out               shl     colorbits, #8                   ' left-justify bits
                        mov     nbits, #24                      ' shift 24 bits (3 x 8) 

:loop                   rcl     colorbits, #1           wc      ' msb --> C
        if_c            mov     bittimer, bit1hi                ' set bit timing  
        if_nc           mov     bittimer, bit0hi                
                        or      outa, txmask                    ' tx line 1  
                        add     bittimer, cnt                   ' sync bit timer  
        if_c            waitcnt bittimer, bit1lo                
        if_nc           waitcnt bittimer, bit0lo 
                        andn    outa, txmask                    ' tx line 0             
                        waitcnt bittimer, #0                    ' hold while low
                        djnz    nbits, #:loop                   ' next bit

                        djnz    nleds, #frame_loop              ' done with all leds?

                        jmp     #reset_delay                    ' get ready for next command

' --------------------------------------------------------------------------------------------------

HX_0000FF               long    $0000FF                         ' byte masks
HX_00FF00               long    $00FF00
HX_FF0000               long    $FF0000

hubpntr                 res     1                               ' pointer to rgb array
ledcount                res     1                               ' # of rgb leds in chain

txmask                  res     1                               ' mask for tx output

bittimer                res     1                               ' timer for reset/bit
addr                    res     1                               ' address of current rgb bit
nleds                   res     1                               ' # of channels to process
colorbits               res     1                               ' rgb for current channel
nbits                   res     1                               ' # of bits to process

t1                      res     1                               ' work vars
t2                      res     1

                        fit     496                                    
{{

  Terms of Use: MIT License

  Permission is hereby granted, free of charge, to any person obtaining a copy of this
  software and associated documentation files (the "Software"), to deal in the Software
  without restriction, including without limitation the rights to use, copy, modify,
  merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so, subject to the following
  conditions:

  The above copyright notice and this permission notice shall be included in all copies
  or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
  PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
  CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
  OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

}}

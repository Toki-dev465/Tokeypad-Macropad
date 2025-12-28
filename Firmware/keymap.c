// Copyright 2023 QMK
// SPDX-License-Identifier: GPL-2.0-or-later
#include QMK_KEYBOARD_H


enum custom_keycodes {
    WORKFLOW = SAFE_RANGE,
    CLOSE_ALL
};

// Store last key pressed
static uint16_t oled_timer = 0;
static char oled_message[32] = "";



bool process_record_user(uint16_t keycode, keyrecord_t *record) {
    // Only handle key press events
    if (record->event.pressed) {

        // ---- OLED message update ----
        #ifdef OLED_ENABLE
        switch (keycode) {
            case KC_MUTE:      snprintf(oled_message, sizeof(oled_message), "Mute"); break;          // Mute key 
            case KC_MPLY:      snprintf(oled_message, sizeof(oled_message), "Play/Pause"); break;    // Play/Pause  
            case KC_MNXT:      snprintf(oled_message, sizeof(oled_message), "Next Track"); break;    // Next track  
            case KC_PSCR:      snprintf(oled_message, sizeof(oled_message), "Print Screen"); break;  // Screnshot when  
            case WORKFLOW:     snprintf(oled_message, sizeof(oled_message), "Workflow"); break;      // Workflow macro 
            case CLOSE_ALL:    snprintf(oled_message, sizeof(oled_message), "Close All"); break;     // Close all apps
        }
        oled_timer = timer_read();  // Reset timer when a key is pressed
        #endif

        // Custom macros
        switch (keycode) {
            case CLOSE_ALL:
                if (record->event.pressed) {
                    // Loop 10 times to close 10 apps
                    for (int i = 0; i < 10; i++) {
                        tap_code16(SS_LALT(KC_F4)); 
                        wait_ms(250);         // Wait for apps to close
                    }
                }
                return false;  // Stop further processing

            case WORKFLOW:
                if (record->event.pressed) {
                    // open VSCode 
                    SEND_STRING(SS_LGUI("r"));
                    wait_ms(300);
                    SEND_STRING("code" SS_TAP(X_ENTER));
                    wait_ms(1000); // Give time to load

                    // open Google Classroom
                    SEND_STRING(SS_LGUI("r"));
                    wait_ms(300);
                    SEND_STRING("start firefox https://classroom.google.com" SS_TAP(X_ENTER)); 
                    wait_ms(500);

                    // open Gmail
                    SEND_STRING(SS_LGUI("r"));
                    wait_ms(300);
                    SEND_STRING("start firefox https://mail.google.com" SS_TAP(X_ENTER)); 
                    wait_ms(500);

                    // open YouTube
                    SEND_STRING(SS_LGUI("r"));
                    wait_ms(300);
                    SEND_STRING("start firefox https://youtube.com" SS_TAP(X_ENTER)); 
                    wait_ms(500);

                    // open Pomodoro timer
                    SEND_STRING(SS_LGUI("r"));
                    wait_ms(300);
                    SEND_STRING("start firefox https://pomofocus.io/" SS_TAP(X_ENTER)); 
                }
                return false;  
        }
    }

    return true;  
}

#ifdef OLED_ENABLE
bool oled_task_user(void) {
    //  reset cursor to start of line
    oled_set_cursor(0, 0);

    // 2. Check Timer
    if (timer_elapsed(oled_timer) > 3000) {
        // Clear the screen 
        
        oled_write_P(PSTR("                "), false); 
    } else {
        // Write the message
        oled_write(oled_message, false);
        
        // Write some extra spaces after to "erase" any previous longer words
        oled_write_P(PSTR("          "), false);
    }
    return false;
}
#endif

// Layout
const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
  [0] = LAYOUT(
    KC_MUTE, KC_MPLY,  KC_MNXT,
    KC_PSCR, WORKFLOW, CLOSE_ALL  
  )
};

// Encoder programming
bool encoder_update_user(uint8_t index, bool clockwise) {
    // Reset timer so the screen wakes up
    oled_timer = timer_read(); 

    if (clockwise) { 
        tap_code(KC_VOLU); 
        snprintf(oled_message, sizeof(oled_message), "Vol Up");
    } else { 
        tap_code(KC_VOLD); 
        snprintf(oled_message, sizeof(oled_message), "Vol Down");
    }
    return true;
}
in main ino file for processing serial commands:
void processSerialCommands() {
    char command[100];
    if (Serial.available()) {
        int len = Serial.readBytesUntil('\n', command, sizeof(command) - 1);
        command[len] = '\0';
        process_command(command);
    }
}

typedef struct {
    const char *cmd;
    void (*handler)(char *args);
} Command;
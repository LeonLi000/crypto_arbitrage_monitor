package utils

import (
    "log"
    "os"
)

var logger = log.New(os.Stdout, "[arb] ", log.LstdFlags|log.Lmicroseconds)

func Logger() *log.Logger {
    return logger
}

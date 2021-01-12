#!/bin/bash

# Echo in various colors.

echo_red() {
    echo -en "\e[31m";
    echo "$@"
    echo -en "\e[0m"
}

echo_green() {
    echo -en "\e[92m";
    echo "$@"
    echo -en "\e[0m"
}

echo_yellow() {
    echo -en "\e[33m";
    echo "$@"
    echo -en "\e[0m"
}

echo_blue() {
    echo -en "\e[34m";
    echo "$@"
    echo -en "\e[0m"
}

echo_magenta() {
    echo -en "\e[95m";
    echo "$@"
    echo -en "\e[0m"
}

# Output the Traxler word mark.

echo_traxler() {
    echo_magenta "████████╗██████╗  █████╗ ██╗  ██╗██╗     ███████╗██████╗ "
    echo_magenta "╚══██╔══╝██╔══██╗██╔══██╗╚██╗██╔╝██║     ██╔════╝██╔══██╗"
    echo_magenta "   ██║   ██████╔╝███████║ ╚███╔╝ ██║     █████╗  ██████╔╝"
    echo_magenta "   ██║   ██╔══██╗██╔══██║ ██╔██╗ ██║     ██╔══╝  ██╔══██╗"
    echo_magenta "   ██║   ██║  ██║██║  ██║██╔╝ ██╗███████╗███████╗██║  ██║"
    echo_magenta "   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝"
}

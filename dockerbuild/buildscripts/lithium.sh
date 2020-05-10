#!/usr/bin/env bash

PROJECTS=(
  BunsenLabs/bunsen-common:10.*:amd64
  BunsenLabs/bunsen-configs:10.*:amd64
  BunsenLabs/bunsen-conky:10.*:amd64
  BunsenLabs/bunsen-docs:10.*:amd64
  BunsenLabs/bunsen-exit:10.*:amd64
  BunsenLabs/bunsen-faenza-icon-theme:10.*:amd64
  BunsenLabs/bunsen-fortune:10.*:amd64
  BunsenLabs/bunsen-images:10.*:amd64
  BunsenLabs/bunsen-keyring:10.*:amd64
  BunsenLabs/bunsen-os-release:10.*:amd64
  BunsenLabs/bunsen-paper-icon-theme:10.*:amd64
  BunsenLabs/bunsen-papirus-icon-theme:10.*:amd64
  BunsenLabs/bunsen-pipemenus:10.*:amd64
  BunsenLabs/bunsen-themes:10.*:amd64
  BunsenLabs/bunsen-thunar:10.*:amd64
  BunsenLabs/bunsen-utilities:10.*:amd64
  BunsenLabs/bunsen-welcome:10.*:amd64
  BunsenLabs/jgmenu:*+bl10-*:amd64,i386,armhf
)

exec dockerbuild batch "${PROJECTS[@]}"

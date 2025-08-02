#!/bin/bash
tshark -r $1 -T json >$2

#!/bin/bash
curl -s -X POST https://chat.dtforg.in/chat \
-H "Content-Type: application/json" \
-d '{"message":"hi"}' > /dev/null 2>&1

# For someone debugging a llama.cpp Mac cluster

A reply you can adapt:

> The DeepSeek clip used a custom MLX runner, not llama.cpp, so I don't have
> equivalent flags from that run. I got Qwen running with Slotstream's explicit SSD
> expert streaming: about 0.57 s/token on a 16 GB M1 Mini in a 64-token test. Can you share your llama.cpp build/commit,
> exact GGUF, command, RAM per Mini, and the first error in the log? There are
> reports of Metal/mmap retaining more model memory than expected, including
> with CPU expert placement and RPC splits. It might be related, but I'd need
> your logs to tell.

Useful upstream reports:

- https://github.com/ggml-org/llama.cpp/issues/27822
- https://github.com/ggml-org/llama.cpp/issues/27667

Neither report establishes the cause of a new failure. Avoid recommending
`--no-mmap` or `--mlock` blindly for a model larger than RAM: changing loading
behavior can defeat the intended SSD paging strategy or require more RAM.
Check the options supported by the exact build before changing its command.

Our Qwen experiment is on one M1 Mini. It does not test distributed inference
or provide measured llama.cpp flags. Slotstream and llama.cpp have different
memory and loading designs.

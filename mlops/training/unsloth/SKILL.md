---
name: unsloth
description: Expert guidance for fast fine-tuning with Unsloth - 2-5x faster training, 50-80% less memory, LoRA/QLoRA optimization
version: 1.0.0
author: Orchestra Research
license: MIT
dependencies: [unsloth, torch, transformers, trl, datasets, peft]
metadata:
  hermes:
    tags: [Fine-Tuning, Unsloth, Fast Training, LoRA, QLoRA, Memory-Efficient, Optimization, Llama, Mistral, Gemma, Qwen]

---

# Unsloth Skill

Comprehensive assistance with unsloth development, generated from official documentation.

## When to Use This Skill

This skill should be triggered when:
- Working with unsloth
- Asking about unsloth features or APIs
- Implementing unsloth solutions
- Debugging unsloth code
- Learning unsloth best practices

## Quick Reference

### Common Patterns

*Quick reference patterns will be added as you use the skill.*

## Reference Files

Two comprehensive documentation files cover all Unsloth content:

- **llms-txt.md** (792k) — Standard documentation with page markers. Best for: general usage, installation, dataset prep, LoRA configs, saving models, benchmarks.
- **llms-full.md** (1.05M) — Extended documentation. Contains: FAQ, tutorials (Qwen3-2507, Phi-4, gpt-oss, etc.), benchmarks, vision/RL guides, troubleshooting, sample outputs.

**Which to use:** Start with `llms-txt.md` for most queries. Use `llms-full.md` for model-specific tutorials, in-depth benchmarks, or when `llms-txt.md` lacks the answer.

- **llms.md** (12k) — Navigation index with links to both docs. Useful for browsing structure.

Use `read_file` to access reference files directly.

## Notes

- Auto-generated from official Unsloth documentation
- llms-full.md contains tutorials + benchmarks not in llms-txt.md




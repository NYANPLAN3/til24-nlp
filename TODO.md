# Actual

- Switch to IBM Granite since coding models are more exact with transcription
- Integrate cheese improvements from nlcheese

# Cheese

- Check if bracket, e.g., electromagnetic pulse (EMP), is always correct, is there
  any other usage of brackets? (check with eval) (ITS ALWAYS CORRECT)
- There are only 7 types of tools, is that true of the test set too? (check with eval) (YES)
  - Theres only arguably 8 types of targets too lol. (INDEED)
  - Can cheese by removing last word if its not in the set? but only remove once
    to avoid removing the entire string if the entire string isnt in set
- Remove heading from schema to vroom fasterer
  - Fallback heading prompt if cheese cannot detect?
  - Separate prompt for fallback case?
- If it can be cheesed, it should be removed from the schema

# Maybe?

- LoRA
- GPT-4o synthetic dataset using all the train examples as context
- Switch to llama.cpp to avoid torch dependency (test the speed)
  - Pointless, even with pure python, speed score is 0.86. With slimmed python, it is 0.82 but 0.04 can be attributed to model regardless of runtime.

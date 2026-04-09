## Requirements

- **Python** 3.12
- Dependencies listed in `requirements.txt`

Install dependencies with:
```bash
pip install -r requirements.txt
```

<details>
<summary>Recommended Setup</summary>

```bash
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

</details>

## Unit Testing

Make sure your code works before pushing

Example of individual tests
```bash
python -m unittest unittests.test_tokenize
```
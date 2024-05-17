# LTP_GPT_scrum_01

```bash
git clone {URL}

cd LTP_GPT_scrum_01

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt

cd src

vi .env

### add .env 
OPENAI_API_KEY=sk-...
### save and exit with ":wq"

uvicorn main:app --reload
```

# Support Ticket Sentiment RAG Bot

Sentiment analysis + RAG bot for customer support tickets, built with the
Anthropic Claude API, deployable to AWS EC2, with results stored in MySQL
and connectable to Power BI.

## Architecture

```
Support tickets (CSV/real data)
   -> Claude API sentiment classification (app/sentiment.py)
   -> Chroma vector store for RAG retrieval (app/embeddings.py)
   -> MySQL for structured storage (app/db.py)
   -> FastAPI endpoints (app/main.py)
   -> Power BI dashboard (connects directly to MySQL)
```

## 1. Local setup (VS Code)

```bash
python3 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Fill in ANTHROPIC_API_KEY and MySQL credentials in .env
```

Make sure MySQL is running locally (or point MYSQL_HOST at RDS), then:

```bash
mysql -u root -p < sql/schema.sql
```

## 2. Generate sample data (since you don't have real tickets yet)

```bash
python data/generate_sample_data.py
```

This creates `data/sample_tickets.csv` with ~150 simulated tickets across
billing, shipping, technical, account, and product categories, with a mix
of sentiments. It includes `true_category`/`true_sentiment` labels so you
can sanity-check Claude's classifications against them.

## 3. Run the ingestion pipeline

```bash
python -m scripts.ingest
```

This classifies each ticket with Claude, writes rows to MySQL, and indexes
embeddings in a local Chroma store (`./chroma_db`).

## 4. Run the API locally

```bash
uvicorn app.main:app --reload
```

Endpoints:
- `POST /analyze` — classify + store a single ticket `{"text": "..."}`
- `POST /ask` — RAG question `{"question": "what are common shipping complaints?"}`
- `GET /tickets` — list all stored tickets
- `GET /health` — health check

Try it at `http://localhost:8000/docs` (FastAPI's built-in Swagger UI).

## 5. Deploy to AWS EC2

1. Launch an Ubuntu EC2 instance (t3.medium+ recommended), open ports 22, 80, 443
2. Upload the project (`scp` or `git clone`) to the instance
3. Run `bash deploy/ec2_setup.sh`
4. Fill in `.env` with real credentials on the instance
5. Install the systemd service: see `deploy/sentiment-bot.service`
6. Configure nginx: see `deploy/nginx.conf`
7. (Optional) Add HTTPS with Certbot: `sudo certbot --nginx -d yourdomain.com`

**MySQL on AWS**: either install MySQL on the same EC2 instance, or
(recommended) use **RDS for MySQL** — easier backups and cleaner Power BI
connectivity. If using RDS, just point `MYSQL_HOST` at the RDS endpoint and
lock the RDS security group down to your EC2 instance's IP.

## 6. Connect Power BI

1. Install the MySQL Connector/NET on the machine running Power BI Desktop
2. In Power BI: **Get Data > Database > MySQL Database**
3. Enter your MySQL/RDS host, port, and `support_tickets` database
4. Use the `tickets` table directly, or the `daily_sentiment_summary` view
   (in `sql/schema.sql`) for a pre-aggregated view that's lighter to refresh
5. Build visuals: sentiment trend over time, category breakdown, volume by day

## 7. MySQL Workbench

Connect Workbench to the same host/port/credentials to browse and query data
manually, run ad-hoc SQL, or export snapshots.

## Notes

- Swap `all-MiniLM-L6-v2` in `app/embeddings.py` for a different embedding
  model if you want higher-quality retrieval at the cost of speed.
- `scripts/ingest.py` paces requests with a small sleep — remove/adjust
  based on your Anthropic rate limits for larger batches.
- Once you have real tickets, just point `scripts/ingest.py` (or a new
  loader) at your actual data source instead of the CSV.

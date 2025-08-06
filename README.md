# Demo Django App with Terraform on GCP 🌐☁️

This is a demo project that combines a Django web application with infrastructure-as-code using Terraform, targeting deployment on Google Cloud Platform (GCP).

---

## 📦 Tech Stack

- **Frontend** Html Templates with Tailwind.css CDN embedded
- **Backend**: Django (Python)
- **Database**: Postgresql
- **Infrastructure**: Terraform
- **Cloud**: Google Cloud Platform (GCP)
- **Tools**: VSCode, Git, Github Actions

---

## 🚀 Project Goals

- Build a minimal Django web app for demonstration and learning purposes.
- Use Terraform to provision GCP infrastructure (e.g., Cloud Run, GKE, Cloud SQL, etc.).
- Showcase modern Dev + DevOps practices in a clean and reproducible setup.

---

## 🛠️ Local Development Setup

```bash
# Clone Repository
git clone https://github.com/nate4101/Django-App.git
cd Django-App

# On Windows
python -m venv .venv
.\.venv\Scripts\activate

python manage.py migrate

create .env file, copy .env.example to .env

python manage.py runserver

Visit: http://127.0.0.1:8000/
```

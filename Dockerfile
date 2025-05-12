FROM odoo:17.0

USER root

COPY ./custom-addons /mnt/custom-addons

COPY requirements.txt .

RUN pip install -r requirements.txt

USER odoo
# -*- coding: utf8 -*-

import os
import logging

from flask import Flask, request, render_template, redirect
from flask_wtf import FlaskForm

from wtforms import StringField, SubmitField, SelectField, IntegerField, FloatField, SelectMultipleField
from wtforms.validators import DataRequired, NumberRange

from google.cloud import bigquery

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'

GCP_PROJECT = os.environ['GOOGLE_CLOUD_PROJECT']


class SearchForm(FlaskForm):
    discipline = SelectMultipleField('Obor projektu (možné zvolit více)', choices=[('', ''), ('AA', 'AA - Filosofie a náboženství'),
                                                       ('AB', 'AB - Dějiny'),
                                                       ('AC', 'AC - Archeologie, antropologie, etnologie'),
                                                       ('AD', 'AD - Politologie a politické vědy'),
                                                       ('AE', 'AE - Řízení, správa a administrativa'),
                                                       ('AF', 'AF - Dokumentace, knihovnictví, práce s informacemi'),
                                                       ('AG', 'AG - Právní vědy'), ('AH', 'AH - Ekonomie'),
                                                       ('AI', 'AI - Jazykověda'),
                                                       ('AJ', 'AJ - Písemnictví, mas–media, audiovize'),
                                                       ('AK', 'AK - Sport a aktivity volného času'),
                                                       ('AL', 'AL - Umění, architektura, kulturní dědictví'),
                                                       ('AM', 'AM - Pedagogika a školství'), ('AN', 'AN - Psychologie'),
                                                       ('AO', 'AO - Sociologie, demografie'),
                                                       ('AP', 'AP - Městské, oblastní a dopravní plánování'),
                                                       ('AQ', 'AQ - Bezpečnost\xa0a ochrana zdraví, člověk – stroj'),
                                                       ('BA', 'BA - Obecná matematika'),
                                                       ('BB', 'BB - Aplikovaná statistika, operační výzkum'),
                                                       ('BC', 'BC - Teorie a systémy řízení'),
                                                       ('BD', 'BD - Teorie informace'),
                                                       ('BE', 'BE - Teoretická fyzika'),
                                                       ('BF', 'BF - Elementární částice a fyzika vysokých energií'),
                                                       ('BG', 'BG - Jaderná, atomová a molekulová fyzika, urychlovače'),
                                                       ('BH', 'BH - Optika, masery a lasery'),
                                                       ('BI', 'BI - Akustika a kmity'),
                                                       ('BJ', 'BJ - Termodynamika'), ('BK', 'BK - Mechanika tekutin'),
                                                       ('BL', 'BL - Fyzika plasmatu a výboje v plynech'),
                                                       ('BM', 'BM - Fyzika pevných látek a magnetismus'),
                                                       ('BN', 'BN - Astronomie a nebeská mechanika, astrofyzika'),
                                                       ('BO', 'BO - Biofyzika'), ('CA', 'CA - Anorganická chemie'),
                                                       ('CB', 'CB - Analytická chemie, separace'),
                                                       ('CC', 'CC - Organická chemie'),
                                                       ('CD', 'CD - Makromolekulární chemie'),
                                                       ('CE', 'CE - Biochemie'),
                                                       ('CF', 'CF - Fyzikální chemie a teoretická chemie'),
                                                       ('CG', 'CG - Elektrochemie'),
                                                       ('CI', 'CI - Průmyslová chemie a chemické inženýrství'),
                                                       ('DA', 'DA - Hydrologie a limnologie'),
                                                       ('DB', 'DB - Geologie a mineralogie'),
                                                       ('DC', 'DC - Seismologie, vulkanologie a struktura Země'),
                                                       ('DD', 'DD - Geochemie'),
                                                       ('DE', 'DE - Zemský magnetismus, geodesie, geografie'),
                                                       ('DF', 'DF - Pedologie'),
                                                       ('DG', 'DG - Vědy o atmosféře, meteorologie'),
                                                       ('DH', 'DH - Báňský průmysl včetně těžby a zpracování uhlí'),
                                                       ('DI', 'DI - Znečištění a kontrola vzduchu'),
                                                       ('DJ', 'DJ - Znečištění a kontrola vody'),
                                                       ('DK', 'DK - Kontaminace a dekontaminace půdy včetně pesticidů'),
                                                       (
                                                           'DL',
                                                           'DL - Jaderné odpady, radioaktivní znečištění a kontrola'),
                                                       ('DM', 'DM - Tuhý odpad a jeho kontrola, recyklace'),
                                                       ('DN', 'DN - Vliv životního prostředí na zdraví'),
                                                       ('DO', 'DO - Ochrana krajinných území'),
                                                       ('EA', 'EA - Morfologické obory a cytologie'),
                                                       ('EB', 'EB - Genetika a molekulární biologie'),
                                                       ('EC', 'EC - Imunologie'),
                                                       ('ED', 'ED - Fyziologie'),
                                                       ('EE', 'EE - Mikrobiologie, virologie'),
                                                       ('EF', 'EF - Botanika'), ('EG', 'EG - Zoologie'),
                                                       ('EH', 'EH - Ekologie – společenstva'),
                                                       ('EI', 'EI - Biotechnologie a bionika'),
                                                       ('FA', 'FA - Kardiovaskulární nemoci včetně kardiochirurgie'),
                                                       (
                                                           'FB',
                                                           'FB - Endokrinologie, diabetologie, metabolismus, výživa'),
                                                       ('FC', 'FC - Pneumologie'),
                                                       ('FD', 'FD - Onkologie a hematologie'),
                                                       ('FE', 'FE - Ostatní obory vnitřního lékařství'),
                                                       ('FF', 'FF - ORL, oftalmologie, stomatologie'),
                                                       ('FG', 'FG - Pediatrie'),
                                                       ('FH', 'FH - Neurologie, neurochirurgie, neurovědy'),
                                                       ('FI', 'FI - Traumatologie a ortopedie'),
                                                       ('FJ', 'FJ - Chirurgie včetně transplantologie'),
                                                       ('FK', 'FK - Gynekologie a porodnictví'),
                                                       ('FL', 'FL - Psychiatrie, sexuologie'), ('FM', 'FM - Hygiena'),
                                                       ('FN',
                                                        'FN - Epidemiologie, infekční nemoci a klinická imunologie'),
                                                       ('FO', 'FO - Dermatovenerologie'),
                                                       ('FP', 'FP - Ostatní lékařské obory'),
                                                       ('FQ', 'FQ - Veřejné zdravotnictví, sociální lékařství'),
                                                       ('FR', 'FR - Farmakologie a lékárnická chemie'),
                                                       ('FS', 'FS - Lékařská zařízení, přístroje a vybavení'),
                                                       ('GA', 'GA - Zemědělská ekonomie'),
                                                       ('GB', 'GB - Zemědělské stroje a stavby'),
                                                       ('GC', 'GC - Pěstování rostlin, osevní postupy'),
                                                       ('GD', 'GD - Hnojení, závlahy, zpracování půdy'),
                                                       ('GE', 'GE - Šlechtění rostlin'),
                                                       ('GF', 'GF - Choroby, škůdci, plevely a ochrana rostlin'),
                                                       ('GG', 'GG - Chov hospodářských zvířat'),
                                                       ('GH', 'GH - Výživa hospodářských zvířat'),
                                                       ('GI', 'GI - Šlechtění a plemenářství hospodářských zvířat'),
                                                       ('GJ', 'GJ - Choroby a škůdci zvířat, veterinární medicina'),
                                                       ('GK', 'GK - Lesnictví'), ('GL', 'GL - Rybářství'),
                                                       ('GM', 'GM - Potravinářství'),
                                                       ('CH', 'CH - Jaderná a kvantová chemie, fotochemie'),
                                                       ('IN', 'IN - Informatika'),
                                                       ('JA', 'JA - Elektronika a optoelektronika, elektrotechnika'),
                                                       ('JB', 'JB - Senzory, čidla, měření a regulace'),
                                                       ('JC', 'JC - Počítačový hardware a software'),
                                                       ('JD', 'JD - Využití počítačů, robotika a její aplikace'),
                                                       ('JE', 'JE - Nejaderná energetika, spotřeba a užití energie'),
                                                       ('JF', 'JF - Jaderná energetika'),
                                                       ('JG', 'JG - Hutnictví, kovové materiály'),
                                                       ('JH', 'JH - Keramika, žáruvzdorné materiály a skla'),
                                                       ('JI', 'JI - Kompositní materiály'),
                                                       ('JJ', 'JJ - Ostatní materiály'),
                                                       ('JK', 'JK - Koroze a povrchové úpravy materiálu'),
                                                       ('JL', 'JL - Únava materiálu a lomová mechanika'),
                                                       ('JM', 'JM - Inženýrské stavitelství'),
                                                       ('JN', 'JN - Stavebnictví'),
                                                       ('JO', 'JO - Pozemní dopravní systémy a zařízení'),
                                                       ('JP', 'JP - Průmyslové procesy a zpracování'),
                                                       ('JQ', 'JQ - Strojní zařízení a nástroje'),
                                                       ('JR', 'JR - Ostatní strojírenství'),
                                                       ('JS', 'JS - Řízení spolehlivosti a kvality, zkušebnictví'),
                                                       ('JT', 'JT - Pohon, motory a paliva'),
                                                       ('JU', 'JU - Aeronautika, aerodynamika, letadla'),
                                                       ('JV', 'JV - Kosmické technologie'),
                                                       ('JW', 'JW - Navigace, spojení, detekce a protiopatření'),
                                                       ('JY', 'JY - Střelné zbraně, munice, výbušniny, bojová vozidla'),
                                                       ('KA', 'KA - Vojenství')], validators=[DataRequired()])
    year_from = IntegerField('Od roku (včetne)', validators=[DataRequired()], default=2000)
    percento = FloatField('Z toho % projektu ve vybranem oboru (od 0.0 do 1.0)', default=0.0, validators=[NumberRange(0.0, 1.0)])
    query_type = SelectField('Typ firem', choices=(('notacr', 'Nikdy nebyli v TAČRu',),('rejtacr', 'Byli, ale nebyli podporeny TAČRrem')
                                                   ), default='notacr')
    submit = SubmitField('Hledaj')


def get_bq_data(discipline, year, query_type, percentage=0.0):
    bq = bigquery.Client(project=GCP_PROJECT)
    if query_type == 'notacr':
        query_spec = f""" ico NOT IN (SELECT idnum FROM `hackujstat.tacr_participants`) """
    else:
        query_spec = """ ico in (SELECT ico FROM (
        SELECT ico, ARRAY_AGG(stav) AS stavy
        FROM (
        SELECT participants.idnum AS ico, headers.projectstate AS stav FROM `hackujstat.tacr_headers` AS headers 
        JOIN `hackujstat.tacr_participants` AS participants ON headers.projectcode = participants.projectcode
        GROUP BY ico, stav
        )
        GROUP BY ico
        )
        WHERE ARRAY_LENGTH(stavy) = 1 AND stavy[OFFSET(0)] = 'Nepodpořen'
        ) """
    query = f"""WITH statsq AS (SELECT nazev_organizace, hlavni_obor as obor, rok_zahajeni
    FROM `hackujstat.CEP` 
    WHERE hlavni_obor <> ''
    AND CAST(rok_zahajeni AS INT64) >= {year} 
    UNION ALL
    SELECT nazev_organizace, vedlejsi_obor as obor, rok_zahajeni
    FROM `hackujstat.CEP` 
    WHERE vedlejsi_obor <> ''
    AND CAST(rok_zahajeni AS INT64) >= {year} 
    UNION ALL
    SELECT nazev_organizace, dalsi_vedlejsi_obor as obor, rok_zahajeni
    FROM `hackujstat.CEP` 
    WHERE dalsi_vedlejsi_obor  <> ''
    AND CAST(rok_zahajeni AS INT64) >= {year} 
    )
    
    SELECT nazev_organizace, ico, obor, c_obor, total_proj, c_obor_norm, c_obor_norm/total_proj AS percents FROM (
    SELECT x.nazev_organizace, ico, obor, c_obor, x.total_proj,IF (c_obor > x.total_proj, x.total_proj, c_obor) AS c_obor_norm FROM (
    SELECT * FROM (
    SELECT nazev_organizace, obor, COUNT(obor) AS c_obor FROM statsq
    WHERE CAST(rok_zahajeni AS INT64) >= {year} 
    GROUP BY nazev_organizace, obor) AS partials
    
    JOIN (
    SELECT nazev_organizace as naz_org, COUNT(*) AS total_proj FROM `hackujstat.CEP` 
    WHERE CAST(rok_zahajeni AS INT64) >= {year} 
    GROUP BY nazev_organizace) totals
    ON partials.nazev_organizace = totals.naz_org
    ) as x
    
    JOIN (
    SELECT nazev_organizace, LPAD(ico, 8, '0') AS ico FROM `hackujstat.CEP` 
    ) as basic_data
    ON basic_data.nazev_organizace = x.nazev_organizace
    )
    WHERE obor IN UNNEST({discipline})
    AND c_obor_norm/total_proj >= {percentage}
    AND total_proj > 0
    AND c_obor_norm > 0
    AND {query_spec}
    GROUP BY nazev_organizace, ico, obor, c_obor, total_proj, c_obor_norm, percents
    ORDER BY c_obor DESC"""
    df = bq.query(query).to_dataframe()
    data = df.to_dict(orient='records')
    return data


@app.route('/', methods=['GET', 'POST'])
def main():
    form = SearchForm()
    results = []
    if form.validate_on_submit():
        discipline = form.discipline.data
        year = form.year_from.data
        percento = form.percento.data
        query_type = form.query_type.data
        logging.info(discipline, year, query_type, percento, )
        results = get_bq_data(discipline, year, query_type, percento)
        return render_template('main.html', form=form, results=results)
    return render_template('main.html', form=form, results=results)


@app.route('/robots.txt', methods=['GET',])
def robots():
    return 'User-agent: * Allow: /'


if __name__ == '__main__':
    logging.getLogger(__name__).setLevel(logging.DEBUG)
    app.run(debug=True)

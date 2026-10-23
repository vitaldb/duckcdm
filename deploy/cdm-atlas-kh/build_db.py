"""koreahealth.ai CDM ATLAS 용 DuckDB: 공개 합성본 synthetic_snuh_cdm(가상 143명) + 그 개념과 조상만 담은 어휘 부분집합.

  python build_db.py <synthetic_snuh_cdm 파케이 폴더> <어휘를 꺼낼 CDM DuckDB> <만들 파일>
환자 표는 공개 합성본 그대로이고, 원내 CDM 에서는 어휘 표(Athena 표준 어휘)만 읽는다. Achilles 는 이어서
`duckcdm achilles <만들 파일>` 로 채운다.
"""
import os
import sys

import duckdb

src, vocab_db, out = sys.argv[1:4]
CDM = ['person', 'observation_period', 'visit_occurrence', 'condition_occurrence', 'drug_exposure',
       'procedure_occurrence', 'measurement', 'observation', 'note']
if os.path.exists(out):
    os.remove(out)
c = duckdb.connect(out)
for t in CDM:
    c.execute(f"CREATE TABLE {t} AS SELECT * FROM read_parquet('{src}/{t}/*.parquet')")
c.execute(f"ATTACH '{vocab_db}' AS v (READ_ONLY)")
# 쓰인 개념: 합성본의 concept 표 + 표들의 *_concept_id 열 전부
cols = c.execute("SELECT table_name, column_name FROM information_schema.columns WHERE table_catalog = current_database() "
                 "AND column_name LIKE '%concept_id'").fetchall()
used = ' UNION '.join([f"SELECT concept_id FROM read_parquet('{src}/concept/*.parquet')"] +
                      [f'SELECT "{col}" FROM {t}' for t, col in cols])
c.execute(f"CREATE TEMP TABLE used AS SELECT DISTINCT concept_id FROM ({used}) WHERE concept_id > 0")
c.execute("CREATE TEMP TABLE keep AS SELECT concept_id FROM used UNION "
          "SELECT ancestor_concept_id FROM v.concept_ancestor WHERE descendant_concept_id IN (SELECT concept_id FROM used)")
c.execute("CREATE TABLE concept AS SELECT * FROM v.concept WHERE concept_id IN (SELECT concept_id FROM keep)")
c.execute("CREATE TABLE concept_ancestor AS SELECT * FROM v.concept_ancestor "
          "WHERE descendant_concept_id IN (SELECT concept_id FROM keep) AND ancestor_concept_id IN (SELECT concept_id FROM keep)")
c.execute("CREATE TABLE concept_relationship AS SELECT * FROM v.concept_relationship "
          "WHERE concept_id_1 IN (SELECT concept_id FROM keep) AND concept_id_2 IN (SELECT concept_id FROM keep)")
c.execute("CREATE TABLE concept_synonym AS SELECT * FROM v.concept_synonym WHERE concept_id IN (SELECT concept_id FROM keep)")
for t in ('vocabulary', 'domain', 'concept_class', 'relationship'):
    c.execute(f"CREATE TABLE {t} AS SELECT * FROM v.{t}")
c.execute("CREATE TABLE cdm_source AS SELECT 'Synthetic-SNUH' cdm_source_name, 'SYNSNUH' cdm_source_abbreviation, "
          "'Seoul National University Hospital (synthetic)' cdm_holder, '공개 합성본 synthetic_snuh_cdm — 가상 환자 143명, 실제 환자 기록이 아니다' "
          "source_description, NULL source_documentation_reference, NULL cdm_etl_reference, DATE '2026-10-21' source_release_date, "
          "current_date cdm_release_date, 'v5.4' cdm_version, 756265 cdm_version_concept_id, "
          "(SELECT vocabulary_version FROM v.vocabulary WHERE vocabulary_id = 'None') vocabulary_version")
# 합성본에 없는 CDM 표는 원내 CDM 의 열 정의로 빈 표를 둔다(Achilles·ATLAS 가 표가 있기를 기대한다)
have = {t for (t,) in c.execute("SELECT table_name FROM duckdb_tables() WHERE database_name = current_database()").fetchall()}
for t in ('death', 'visit_detail', 'device_exposure', 'specimen', 'condition_era', 'drug_era', 'dose_era', 'care_site',
          'location', 'provider', 'payer_plan_period', 'cost', 'fact_relationship', 'note_nlp', 'episode', 'metadata'):
    if t not in have and c.execute(f"SELECT count(*) FROM duckdb_tables() WHERE database_name = 'v' AND table_name = '{t}'").fetchone()[0]:
        c.execute(f"CREATE TABLE {t} AS SELECT * FROM v.{t} LIMIT 0")
c.execute("DETACH v")
for (t,) in c.execute("SELECT table_name FROM duckdb_tables() WHERE database_name = current_database() ORDER BY 1").fetchall():
    print(t, c.execute(f'SELECT count(*) FROM {t}').fetchone()[0])
c.execute('CHECKPOINT')

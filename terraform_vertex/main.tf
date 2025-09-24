provider "google" {
    project=var.project_id
    region=var.region
}


resource "google_bigquery_dataset" "dataset_v1"{
    dataset_id = var.dataset_id
    project = var.project_id
    location = var.region
}


resource "google_bigquery_table" "table_v1"{
    table_id = var.table_id
    dataset_id = var.dataset_id
    project = var.project_id

    schema = jsonencode([
        {
            name="age",
            type="INTEGER"
            mode="REQUIRED"
        },
        {
            name="workclass",
            type="STRING"
            mode="REQUIRED"
        },
        {
            name="occupation",
            type="STRING"
            mode="REQUIRED"
        }
    ])
}



resource "google_bigquery_dataset_iam_binding" "dataset_acces"{
    dataset_id = var.dataset_id
    project = var.project_id

    role = "roles/bigquery.dataViewer"
    members = [
        "serviceAccount:mlops-process@mlops12-469915.iam.gserviceaccount.com"
    ]
}


resource "google_bigquery_routine" "cencus_filter_by_age" {
  routine_id = var.routine_id
  dataset_id = var.dataset_id
  project    = var.project_id

  definition_body = <<-SQL
    BEGIN
      INSERT INTO `mlops12-469915.github.census_by_age`
      SELECT age, workclass, occupation
      FROM `bigquery-public-data.ml_datasets.census_adult_income`
      WHERE age < input_age;
    END;
  SQL

  routine_type = "PROCEDURE"

  arguments {
    name      = "input_age"
    data_type     = jsonencode({ "typeKind" : "INT64" })
  }
}

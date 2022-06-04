Table incident_movility_history as tmh {
  id                      numeric [pk]
  source                  numeric
  type                    numeric
  state                   numeric
  priority                numeric
  gravity                 numeric
  class                   numeric
  varchar                 numeric
  actor                   numeric
  public                  boolean
  latitude                numeric
  longitude               numeric
  location                varchar
  id_user                 numeric
  name_user               varchar
  time_stamp              varchar
  broker_id               numeric
  implicated              numeric
  address                 varchar
  updatedate              varchar
  zone_id                 numeric
  orient                  numeric
  require_support         numeric
  incident_time           varchar
  id_user_modified        numeric
  name_user_modified      varchar
  type_others             varchar
}

Table incident_movility_description as imd {
  id                      numeric [pk]
  id_incident             numeric [ref: < tmh.id]
  description             varchar
  id_user                 numeric
  name_user               varchar
  time_stamp              varchar
 }
 
Table incident_categories as ic {
  id                      numeric [pk] 
  category_type           numeric
  category_state          boolean
  category_name           varchar
  parent_id               numeric [ref: - ic.id]
} 

Table incidentes_implicated as ii {
  id                      numeric [pk]
  incident_id             numeric [ref: < tmh.id]
  implicated_type         numeric
  injured_count           numeric
  dead_count              numeric
}
import edu.chop.cbmi.dataExpress.dsl.ETL._
import edu.chop.cbmi.dataExpress.dsl.ETL
import edu.chop.cbmi.dataExpress.dsl.stores.SqlDb
import edu.chop.cbmi.dataExpress.dataModels.RichOption._

register store SqlDb("conf/dcm4cheedb.properties") as "source"
register store SqlDb("conf/djangodb.properties") as "target1"
register store SqlDb("conf/djangodb.properties") as "target2"


val study_table = """select study_iuid as original_study_uid,
                     accession_no as accession_no,
                     study_datetime as study_date from study"""

val append_table = """select original_study_uid, accession_no, study_date,
                      date('now') as created,
                      date('now') as modified,
                      0 as high_risk_flag,
                      0 as image_published,
                      1 as requested,
                      0 as exclude from study_staging_import where original_study_uid not in
                      (select original_study_uid from staging_radiologystudy) and accession_no not null"""

commit_on_success("target1") {
    copy query study_table from "source" to "target1" create "study_staging_import"
}

commit_on_success("target2") {
   copy query append_table from "target1" to "target2" append "staging_radiologystudy"
}

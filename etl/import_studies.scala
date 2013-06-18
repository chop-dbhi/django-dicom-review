import edu.chop.cbmi.dataExpress.dsl.ETL._
import edu.chop.cbmi.dataExpress.dsl.ETL
import edu.chop.cbmi.dataExpress.dsl.stores.SqlDb
import edu.chop.cbmi.dataExpress.backends._
import edu.chop.cbmi.dataExpress.dataModels.RichOption._

register store SqlDb("conf/pacsdb.properties") as "source"
register store SqlDb("conf/djangodb.properties") as "target1"
val target2Store = SqlDb("conf/djangodb.properties")
register store target2Store as "target2"

val study_table = """select study_iuid as original_study_uid,
                     accession_no as accession_no,
                     study_datetime as study_date from study"""

// This should work for postgres, mysql and sqlite but is not exhaustive
val time = target2Store match {
  case s:SqlDb => s.backend match {
    case sl:SqLiteBackend => "date('now')"
    case _ =>"now()"
  }
  case _ => "now()"
}

val append_table = s"""select original_study_uid, accession_no, study_date,
                      $time as created,
                      $time as modified,
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

target2Store.backend.connect()
target2Store.backend.execute("drop table study_staging_import")
target2Store.backend.commit()

module Models where

import Dict exposing (Dict)

type Action
 = NoOp
 --| GetJobs
 | InitiateJobsFromJson String
 | ShowInitialJobs (Maybe Jobs)
 | SortJobs JobField
 | ToggleFilter JobField String
 | FromStorage String
 | HideWelcome

type alias Job =
  { title : String
  , organization : String
  , division : String
  , urlDetail : String
  , dateClosing : String
  , salaryWaged : Bool
  , salaryAmount : Float
  , region : String
  , datePosted : String
  }

type JobField
  = Title
  | Organization
  | Salary
  | ClosingDate
  | PostingDate
  | Region
  | URL

type alias Jobs = List Job

type alias Model =
  { jobs : Maybe Jobs
  , jobFilter : Filter
  , fromStorage : String
  , showWelcome : Bool
  }

type alias Filter =
  { allRegions : Dict String (List String)
  , allOrgs : Dict String String
  , visibleRegions : List String
  , visibleOrgs : List String
  }

getOrgRegion : String -> Dict String String -> String
getOrgRegion org allOrgs =
  Dict.get org allOrgs |> Maybe.withDefault ""

sortOnCriteria : JobField -> List Job -> List Job
sortOnCriteria f js = List.sortWith (compareJob f) js

sortJobs : JobField -> Maybe Jobs -> Maybe Jobs
sortJobs criteria jobs =
  let currentJobsList = Maybe.withDefault [] jobs
      sortedCurrentList = sortOnCriteria criteria currentJobsList
  in
    if currentJobsList == sortedCurrentList
      then Just (List.reverse sortedCurrentList)
      else Just sortedCurrentList

compareJob : JobField -> Job -> Job -> Order
compareJob f j k =
  -- we use a special sorting function to deal with secondary sorting fields.
  -- on Chrome, List.sortBy acted nondeterministically when comparing jobs with
  -- identical fields in currentList and sortedCurrentList.
  -- With this solution, if the compared fields on two jobs are equal, we compare the URL
  -- fields to determine sort order. URLs are guaranteed to be unique.
  -- (A job won't be entered into the database unless its URL is unique.)
  let divorg a = a.organization ++ a.division
      comp af bf a b = if af == bf then compareJob URL a b else if af > bf then GT else LT
  in
    case f of
      URL ->
        comp j.urlDetail k.urlDetail j k
      Title ->
        comp j.title k.title j k
      Organization ->
        comp (divorg j) (divorg k) j k
      Salary ->
        comp j.salaryAmount k.salaryAmount j k
      PostingDate ->
        comp j.datePosted k.datePosted j k
      ClosingDate ->
        comp j.dateClosing k.dateClosing j k
      _ ->
        comp j.urlDetail k.urlDetail j k

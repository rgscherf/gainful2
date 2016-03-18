module Models where

import Dict exposing (Dict)

type Action
 = NoOp
 | GetJobs
 | ShowInitialJobs (Maybe Jobs)
 | SortJobs JobField
 | ToggleFilter JobField String
 | FromStorage String

type alias Job =
  { title : String
  , organization : String
  , division : String
  , urlDetail : String
  , dateClosing : String
  , salaryWaged : Bool
  , salaryAmount : Float
  , region : String
  }

type JobField
  = Title
  | Organization
  | Salary
  | ClosingDate
  | Region

type alias Jobs = List Job

type alias Model =
  { jobs : Maybe Jobs
  , jobFilter : Filter
  , fromStorage : String
  }

type alias Filter =
  { allRegions : Dict String (List String)
  , allOrgs : Dict String String
  , visibleRegions : List String
  , visibleOrgs : List String
  }

sortJobs : JobField -> Maybe Jobs -> Maybe Jobs
sortJobs criteria jobs = 
  let currentJobsList = Maybe.withDefault [] jobs
      sortedCurrentList =
        let divorg j = j.organization ++ j.division
        in
        case criteria of
          Title -> List.sortBy .title currentJobsList
          Organization -> List.sortBy divorg currentJobsList
          Salary -> List.sortBy .salaryAmount currentJobsList
          ClosingDate -> List.sortBy .dateClosing currentJobsList
          _ -> currentJobsList
  in
    if currentJobsList == sortedCurrentList
      then Just (List.reverse sortedCurrentList)
      else Just sortedCurrentList

module Models where

type alias Job =
  { title : String
  , organization : String
  , division : String
  , urlDetail : String
  , dateClosing : String
  , salaryWaged : Bool
  , salaryAmount : Float
  }

type SortingCriteria
  = Title
  | Organization
  | Salary
  | ClosingDate

type alias Jobs = List Job

type alias Model = {jobs : Maybe Jobs}

type Action
 = NoOp
 | GetJobs
 | ShowJobs (Maybe Jobs)
 | SortJobs SortingCriteria


sortJobs : SortingCriteria -> Model -> Model
sortJobs criteria model =
  let currentJobsList =
        case model.jobs of
          Nothing -> []
          Just js -> js
      sortedCurrentList =
        let divorg j = j.organization ++ j.division
        in
        case criteria of
          Title -> List.sortBy .title currentJobsList
          Organization -> List.sortBy divorg currentJobsList
          Salary -> List.sortBy .salaryAmount currentJobsList
          ClosingDate -> List.sortBy .dateClosing currentJobsList
  in
    if currentJobsList == sortedCurrentList
      then { model | jobs = Just (List.reverse sortedCurrentList) }
      else { model | jobs = Just sortedCurrentList }

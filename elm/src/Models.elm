module Models where

import Set

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
  }

type alias Filter =
  { organizations : List (String, Bool)
  , regions : List (String, Bool)
  }

type Action
 = NoOp
 | GetJobs
 | ShowInitialJobs (Maybe Jobs)
 | SortJobs JobField
 | ToggleFilter JobField String
 | ChangeAllFilter JobField Bool


makeFilter : Model -> Model
makeFilter m =
  let newFilter = { organizations = filList .organization
                  , regions = filList .region
                  }
      filList field = List.map (\s -> (s, True))
                      <| Set.toList
                      <| Set.fromList
                      <| List.map (\j -> field j)
                      <| Maybe.withDefault [] m.jobs
  in {m | jobFilter = newFilter}

sortJobs : JobField -> Model -> Model
sortJobs criteria model =
  let currentJobsList = Maybe.withDefault [] model.jobs
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
      then { model | jobs = Just (List.reverse sortedCurrentList) }
      else { model | jobs = Just sortedCurrentList }

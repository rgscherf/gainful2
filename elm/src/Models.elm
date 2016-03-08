module Models where

import Dict exposing (Dict)

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

-- a region's name is associated with a "visible" flag
-- and a dict of (name, visible) for its associated organizations
type alias Filter = Dict String (Bool, Dict String Bool)

type Action
 = NoOp
 | GetJobs
 | ShowInitialJobs (Maybe Jobs)
 | SortJobs JobField
 | ToggleFilter JobField String
 | ChangeAllFilter JobField Bool

makeFilter : Filter -> Model -> Model
makeFilter f m =
  {m | jobFilter = List.foldr makeFilter' f <| Maybe.withDefault [] m.jobs }

makeFilter' : Job -> Filter -> Filter
makeFilter' j f=
  case Dict.get j.region f of
    Nothing ->
      Dict.insert j.region (True, Dict.singleton j.organization True) f
    Just (b, os) ->
      case Dict.get j.organization os of
        Nothing -> Dict.update j.region (updateRegion j.organization) f
        Just o -> f

updateRegion : String -> Maybe (Bool, Dict String Bool) -> Maybe (Bool, Dict String Bool)
updateRegion str mv =
  case mv of
    Just (b, d) ->
      Just (b, Dict.insert str True d)
    Nothing ->
      Nothing


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

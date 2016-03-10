module Main where

import Html exposing (..)
import Http
import StartApp
import Effects exposing (Effects)
import Task
import Json.Decode as D exposing ((:=), Decoder)
import Dict
import Set

import Models exposing (..)
import Site exposing (..)

---------
-- WIRING
---------

app : StartApp.App Model
app = StartApp.start
  { init = init
  , view = view
  , update = update
  , inputs = []
  }

main : Signal Html
main = app.html

startFilter : Filter
startFilter =
  { allRegions = Dict.empty
  , allOrgs = Dict.empty
  , visibleRegions = []
  , visibleOrgs = []
  }

startModel : Model
startModel =
  { jobs = Nothing
  , jobFilter = startFilter
  }

init : (Model, Effects Action)
init = (startModel, getJobs)

port tasks : Signal (Task.Task Effects.Never ())
port tasks = app.tasks


---------
-- UPDATE
---------

update : Action -> Model -> (Model, Effects Action)
update action model =
  case action of
    SortJobs s ->
      (sortJobs s model, Effects.none)
    NoOp ->
      (model, Effects.none)
    GetJobs ->
      ({model | jobs = Nothing}, getJobs)
    ShowInitialJobs maybeJobs ->
      let newModel = makeFilter model.jobFilter {model | jobs = maybeJobs}
      in (sortJobs Organization newModel, Effects.none)
    ToggleFilter field identifier ->
      ( { model | jobFilter = toggleFilter field identifier model.jobFilter }
      , Effects.none
      )
    ChangeAllFilter field state ->
      ( model, Effects.none )


toggleFilter : JobField -> String -> Filter -> Filter
toggleFilter field identifier fil =
  case field of
    Region ->
      if List.member identifier fil.visibleRegions
      then
        { fil
          -- make region not visible
          | visibleRegions = List.filter (\x -> x /= identifier) fil.visibleRegions
          -- make all orgs connected to this region not visible
          , visibleOrgs = List.filter
                            (\x -> not <| List.member x
                              (Maybe.withDefault [] <| Dict.get identifier fil.allRegions))
                          fil.visibleOrgs
        }
      else
        { fil
          -- make region active
          | visibleRegions = identifier :: fil.visibleRegions
          -- make all orgs connected to this region active
          , visibleOrgs = Set.toList
                            <| Set.fromList
                            <| (Maybe.withDefault [] <| Dict.get identifier fil.allRegions) ++ fil.visibleOrgs
        }
    Organization ->
      if List.member identifier fil.visibleOrgs
      then -- orgianization is currently visible
           -- make org not visible
           -- if no orgs in this org's region are visible, ensure it's not visible.
           fil
      else -- organization is currently NOT visible
           -- make org visible
           -- if all orgs in this org's region are visible, ensure it's visible.
           fil
    _ -> fil -- we only filter on Region and Organization





-- toggleFilter : JobField -> String -> Filter -> Filter
-- toggleFilter field identifier fil =
--   let
--     visible x ls =
--       if List.member x ls
--       then List.filter (\a -> a /= x) ls
--       else x :: ls
--   in
--     case field of
--       Region ->
--         { fil | visibleRegions = visible identifier fil.visibleRegions }
--           |> negateOrgs
--       Organization ->
--         { fil | visibleOrgs = visible identifier fil.visibleOrgs }
--       _ -> fil
--
-- negateOrgs : Filter -> Filter
-- negateOrgs f =
--     { f | visibleOrgs = List.filter (\x -> List.member (Dict.get x f.allOrgs |> Maybe.withDefault "" ) f.visibleRegions) f.visibleOrgs }

makeFilter : Filter -> Model -> Model
makeFilter f m =
  {m | jobFilter = makeAllEntitiesVisible <| List.foldr makeFilter' f <| Maybe.withDefault [] m.jobs }

makeAllEntitiesVisible : Filter -> Filter
makeAllEntitiesVisible f =
  { f | visibleOrgs = Dict.keys f.allOrgs
      , visibleRegions = Dict.keys f.allRegions
  }

makeFilter' : Job -> Filter -> Filter
makeFilter' j f =
  case Dict.get j.region f.allRegions of
    Nothing ->
      { f | allRegions = Dict.insert j.region [j.organization] f.allRegions
          , allOrgs = Dict.insert j.organization j.region f.allOrgs
      }
    Just os ->
      case List.member j.organization os of
        True ->
          f
        False ->
          { f | allOrgs = Dict.insert j.organization j.region f.allOrgs
              , allRegions = Dict.update j.region (\xs -> Just <| j.organization :: (Maybe.withDefault [] xs)) f.allRegions
          }

----------
-- EFFECTS
----------

jobsUrl : String
jobsUrl = "http://localhost:8000/jobs/"

getJobs : Effects Action
getJobs =
  Http.get decodeJobList jobsUrl
    |> Task.toMaybe
    |> Task.map ShowInitialJobs
    |> Effects.task


decodeJob : Decoder Job
decodeJob =
  D.object8 Job
    ("title" := D.string)
    ("organization" := D.string)
    ("division" := D.string)
    ("url_detail" := D.string)
    ("date_closing" := D.string)
    ("salary_waged" := D.bool)
    ("salary_amount" := D.float)
    ("region" := D.string)

decodeJobList : Decoder Jobs
decodeJobList = D.list decodeJob

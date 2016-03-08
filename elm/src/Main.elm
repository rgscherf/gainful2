module Main where

import Html exposing (..)
import Http
import StartApp
import Effects exposing (Effects)
import Task
import Json.Decode as D exposing ((:=), Decoder)
import Dict

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

startModel : Model
startModel =
  { jobs = Nothing
  , jobFilter = Dict.empty
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
      ( model, Effects.none )
    ChangeAllFilter field state ->
      ( model, Effects.none )





-- changeAllFilter : JobField -> Bool -> Filter -> Filter
-- changeAllFilter field state fil =
--   let changeAllStates state ls =
--         List.map (\(st, bo) -> (st, state)) ls
--   in
--     case field of
--       Organization -> { fil | organizations = changeAllStates state fil.organizations }
--       Title -> fil
--       Salary -> fil
--       ClosingDate -> fil
--       Region -> { fil | regions = changeAllStates state fil.regions }
--
-- updateFilter : JobField -> String -> Filter -> Filter
-- updateFilter field identifier fil =
--   let toggleElement i ls =
--         List.map (\(st, bo) ->
--                   if st /= identifier
--                   then (st, bo)
--                   else (st, not bo))
--                  ls
--   in
--     case field of
--       Organization ->
--         { fil | organizations = toggleElement identifier fil.organizations }
--       Title -> fil
--       Salary -> fil
--       ClosingDate -> fil
--       Region ->
--         { fil | regions = toggleElement identifier fil.regions }
--
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

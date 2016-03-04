module Main where

import Html exposing (..)
import Http
import StartApp
import Effects exposing (Effects)
import Task
import Json.Decode as D exposing ((:=), Decoder)

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
  , jobFilter = { organizations = [] }
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
      let newModel = makeFilter {model | jobs = maybeJobs}
      in (sortJobs Organization newModel, Effects.none)
    ToggleFilter field identifier -> ({model | jobFilter = updateFilter field identifier model.jobFilter}, Effects.none )

updateFilter : SortingCriteria -> String -> Filter -> Filter
updateFilter field identifier fil =
  let toggleElement i ls =
        List.map (\(st, bo) ->
                  if st /= identifier
                  then (st, bo)
                  else (st, not bo))
                 ls
  in
  case field of
    Organization ->
      { fil | organizations = toggleElement identifier fil.organizations }
    Title -> fil
    Salary -> fil
    ClosingDate -> fil

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
  D.object7 Job
    ("title" := D.string)
    ("organization" := D.string)
    ("division" := D.string)
    ("url_detail" := D.string)
    ("date_closing" := D.string)
    ("salary_waged" := D.bool)
    ("salary_amount" := D.float)

decodeJobList : Decoder Jobs
decodeJobList = D.list decodeJob

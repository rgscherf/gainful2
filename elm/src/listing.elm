import Html exposing (..)
import Http
import StartApp
import Effects exposing (Effects)
import Task
import Html.Events exposing (..)
import Html.Attributes exposing (..)
import Json.Decode as D exposing ((:=), Decoder)

---------
-- WIRING
---------

jobsUrl = "./jobs.json"

app = StartApp.start
  { init = init
  , view = view
  , update = update
  , inputs = []
  }

main = app.html

init = ({jobs = Nothing}, getJobs)

port tasks : Signal (Task.Task Effects.Never ())
port tasks = app.tasks


--------
-- TYPES
--------

type Action
 = NoOp
 | GetJobs
 | ShowJobs (Maybe Jobs)
 | SortJobs SortingCriteria

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
    ShowJobs maybeJobs ->
      ({model | jobs = maybeJobs}, Effects.none)


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


---------
-- VIEWS
---------

view address model =
  div
    []
    [
      viewJobs address model.jobs
    ]

viewJobs address maybeJobs =
  let
      tbody =
        case maybeJobs of
            Nothing -> [ tr [] [] ]
            Just jobs -> List.concatMap individualJob jobs
  in
    table [align "center", style [("width", "90%")]]
      (
        [ tr []
          [ th [onClick address (SortJobs Title)] [text "Title"]
          , th [onClick address (SortJobs Organization)] [text "Organization"]
          , th [onClick address (SortJobs Salary)] [text "Salary/Wage"]
          , th [onClick address (SortJobs ClosingDate)] [text "Closing Date"]
          ]
        ]
        ++ tbody
      )

individualJob : Job -> List Html
individualJob job =
  let stringSalary = toString <| if job.salaryWaged then job.salaryAmount else toFloat <| round job.salaryAmount
      postfix = if job.salaryWaged then " /hr" else " /yr"
      orgAndDiv = if job.division /= "" then job.organization ++ ", " ++ job.division else job.organization
  in
  [tr []
    [ td [] [a
              [href job.urlDetail]
              [text job.title]
            ]
    , td [] [text <| orgAndDiv]
    , td [align "right"] [text (if job.salaryAmount == 0 then "--" else "$ " ++ stringSalary ++ postfix)]
    , td [align "right"] [text job.dateClosing]
    ]
  ]



----------
-- EFFECTS
----------

getJobs : Effects Action
getJobs =
  Http.get decodeJobList jobsUrl
    |> Task.toMaybe
    |> Task.map ShowJobs
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

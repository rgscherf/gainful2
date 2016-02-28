import Html exposing (..)
import Http
import StartApp
import Effects exposing (Effects)
import Task
import Html.Events exposing (..)
import Html.Attributes exposing (..)
import Json.Decode as D exposing ((:=), Decoder)

jobsUrl = "./jobs.json"

app = StartApp.start
  { init = init
  , view = view
  , update = update
  , inputs = []
  }

main = app.html

port tasks : Signal (Task.Task Effects.Never ())
port tasks = app.tasks

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

type alias Jobs = List Job

type alias Model = {jobs : Maybe Jobs}

init = ({jobs = Nothing}, getJobs)

update action model =
  let jobList =
      case model.jobs of
        Nothing -> []
        Just list -> list
  in
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
sortJobs sorting model =
  let currentJobs =
        case model.jobs of
          Nothing -> []
          Just js -> js
      sortType =
        case sorting of
          Title -> .title
          Organization -> .organization
      sortedCurrentList = List.sortBy sortType currentJobs

  in
    if currentJobs == sortedCurrentList
      then { model | jobs = Just (List.reverse currentJobs) }
      else { model | jobs = Just sortedCurrentList }


view address model =
  div
    []
    -- [ button [onClick address GetJobs] [text "Click for jobs!" ]

    -- HTML for top nav
    -- HTML for filter box
    [
      viewJobs address model.jobs
    ]

individualJob : Job -> List Html
individualJob job =
  let stringSalary = toString <| if job.salaryWaged then job.salaryAmount else toFloat <| round job.salaryAmount
      postfix = if job.salaryWaged then " /hour" else " /year"
  in
  [tr []
    [ td [] [a
              [href job.urlDetail]
              [text job.title]
            ]
    , td [] [text job.organization]
    , td [] [text (if job.salaryAmount == 0 then "???" else "$" ++ stringSalary ++ postfix)]
    , td [] [text job.dateClosing]
    ]
  ]

viewJobs address maybeJobs =
  let
      tbody =
        case maybeJobs of
            Nothing ->
              [tr [] [ td [] []
                     , td [] []
                     , td [] []
                     , td [] []
                     , td [] []
                     ]
              ]
            Just jobs ->
              List.concatMap individualJob jobs
  in
    table [style [("width", "95%")]]
      (
        [ tr []
          [ th [onClick address (SortJobs Title)] [text "Title"]
          , th [onClick address (SortJobs Organization)] [text "Organization"]
          , th [onClick address (SortJobs Organization)] [text "Division/Department"]
          , th [onClick address (SortJobs Organization)] [text "Salary/Wage"]
          , th [onClick address (SortJobs Organization)] [text "Closing Date"]
          ]
        ]
        ++ tbody
      )


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

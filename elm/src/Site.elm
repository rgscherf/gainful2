module Site where

import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (..)
import Markdown
import Dict exposing (Dict)
import String

import Models exposing (..)

------------
-- MAIN VIEW
------------

view : Signal.Address Action -> Model -> Html
view address model =
  div
    []
    [
      navBar
    , spacer
    , div [] <| filterBox address model.jobFilter
    --, spacer
    --, newsletter
    , spacer    
    , viewJobs address model.jobFilter model.jobs
    , spacer
    ]

-- NAV

navBar : Html
navBar =
  nav [] [ span [class "logo"] [text "Gainful"]
         , a [href "http://www.google.com"]
             [i [class "fa fa-2x fa-fw fa-info-circle nav-icon"] []]
         , a [href "http://www.github.com/rgscherf/gainful2"]
             [i [class "fa fa-2x fa-fw fa-github nav-icon"] []]
         , a [href "http://www.twitter.com/rgscherf"]
             [i [class "fa fa-2x fa-fw fa-twitter nav-icon"] []]
         ]

-- SPACER
spacer : Html
spacer = div [class "spacer"] []

-- NEWSLETTER
newsletter : Html
newsletter =
  div [class "filterwrapper shadow"] [text <| "Want daily updates with these filter settings? Newsletter coming soon!"]

-- FILTERBOX

filterBox : Signal.Address Action -> Filter -> List Html
filterBox a f =
  let
    accessor field fil =
      if field == Organization
      then .visibleOrgs fil
      else .visibleRegions fil
    btn fil field x =
      button
        [ class <| if List.member x <| accessor field fil
                   then "visible"
                   else "notVisible"
        , onClick a (ToggleFilter  field x) ]
        [ text x ]
    orgRoster = 
      Dict.keys f.allOrgs
        |> List.filter (\a -> List.member (getOrgRegion a f.allOrgs) f.visibleRegions) 
        |> List.sortBy (\a -> getOrgRegion a f.allOrgs)
        |> List.map (btn f Organization)
    regionRoster = 
       List.map (btn f Region)
        <| List.sort
        <| Dict.keys f.allRegions 
  in
    [div [class "filterwrapper shadow"]
      [ div
        [ id "filterannounce" ]
        [ text "Filter by..." ]
      , div
        [id "filtertable"]
        [ table
          []
          [ tr [] -- filter for regions
            [ td [class "filtertitle"] [text "regions:"]
            , td [] regionRoster
            ]
          , tr [class "blankrow"] [td [colspan 2] []]
          , tr [] -- filter for organizations
            [ td [class "filtertitle"] [text "organizations:"]
            , td [] orgRoster 
            ]
          ]
        ]
      --, div -- newsletter button
      --    [id "filternewsletter"]
      --    [ button [id "newsletterbutton"] [text "Save filters to daily newsletter"]]
      ]
    ]


-- Job table

viewJobs : Signal.Address Action -> Filter -> Maybe Jobs -> Html
viewJobs address fil maybeJobs =
  let
    jobs =
      List.filter (\j -> List.member j.organization fil.visibleOrgs)
      <| Maybe.withDefault [] maybeJobs
    shaded = List.concat <| List.repeat (List.length jobs) [True, False]
    jobAndClass = List.map2 (,) shaded jobs
    tbody = List.concatMap individualJob jobAndClass
    sortIndicator f =
      if sortOnCriteria f jobs == jobs
      then i [class "fa fa-arrow-down"] []
      else
        if sortOnCriteria f  jobs == List.reverse jobs
        then i [class "fa fa-arrow-up"] []
        else i [class "fa fa-arrow-up", style [("opacity", "0")]] []
  in
    table [id "jobtable", class "shadow"]
      (
        [ tr [class "jobTableHeader"]
          [ th [onClick address (SortJobs Organization), class "leftHead"] [text "Organization ", sortIndicator Organization]
          , th [onClick address (SortJobs Title), class "leftHead"] [text "Title ", sortIndicator Title]
          , th [onClick address (SortJobs Salary), class "rightHead"] [sortIndicator Salary, text " Salary"]
          , th [onClick address (SortJobs PostingDate), class "rightHead"] [sortIndicator PostingDate, text " Posted"]
          , th [onClick address (SortJobs ClosingDate), class "rightHead"] [sortIndicator ClosingDate, text " Closing"]
          ]
        ]
        ++ tbody
      )

individualJob : (Bool, Job) -> List Html
individualJob (shaded, job) =
  let
      orgAndDiv = if job.division /= "" then job.organization ++ ", " ++ job.division else job.organization
      rowClass = if shaded then "shadedRow" else "unshadedRow"
      shortTitle title = if String.contains "(" title then Maybe.withDefault "" <| List.head <| String.split "(" title else title
  in
  [tr [class rowClass]
    [
      td [] [text <| orgAndDiv]
    , td [] [a
              [href job.urlDetail]
              [text <| shortTitle job.title] -- sections of job titles in parens are seldom useful
            ]
    , td [align "right"] [text <| salary job.salaryAmount job.salaryWaged]
    , td [align "right"] [text <| String.dropLeft 5 job.datePosted]
    , td [align "right"] [text <| String.dropLeft 5 job.dateClosing]
    ]
  ]

salary : Float -> Bool -> String
salary amount waged =
  let stringSalary = if waged then toString amount else addCommas amount
      postfix = if waged then " /h" else " /y"
  in
    if amount == 0 then "--" else "$ " ++ stringSalary ++ postfix

addCommas : Float -> String
addCommas amt =
  let start = String.reverse <| toString <| round amt
      len = String.length start
  in
    if (len < 4) then String.reverse start
    -- public service salaries will never > $999,999
    else String.reverse <| (String.left 3 start) ++ "," ++ (String.dropLeft 3 start)


-- about page

aboutMessage : Html
aboutMessage = Markdown.toHtml """

# What is Gainful?

Job searching is bad. Government websites are bad. This makes searching for government jobs extra bad.

Gainful makes government job postings simple and sane. 
Every day, it finds all the newest postings and present them in a table. 
  You can filter and sort listings however you want, and save your results as a daily email newsletter.

No signups, no ads. It could not be easier.

## What job sites does Gainful search?

Glad you asked. Gainful searches the following sources:

- City of Toronto
- City of Victoria
- City of Mississauga
- Ontario Public Service in the GTA (TODO)
- ...etc

## Can I help?

[twitter]: http://www.twitter.com/rgscherf

Yes! [Get in touch][twitter] or make a [pull request](http://www.github.com/rgscherf/gainful2).

## Who wrote Gainful?

Gainful is written by Robert Scherf. He's looking for a job--[hire him][twitter]!

"""

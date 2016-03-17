module Site where

import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (..)
import Markdown
import Dict
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
    -- , div [] [text <| toString model.jobFilter]
    , div [class "spacer"] []
    , div [] <| filterBox address model.jobFilter
    , div [class "spacer"] []
    , viewJobs address model.jobFilter model.jobs
    , div [class "spacer"] []
    , div [class "spacer"] []
    , div [class "spacer"] []
    , div [class "spacer"] []
    -- , aboutMessage
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
  in
    [div [id "filterwrapper", class "shadow"]
      [ div
        [id "filtertable"]
        [table []
          [ tr []
            [ td [class "filtertitle"] [text "Filter by region:"]
            , td [] <| ( List.map (btn f Region)
                        <| List.sort
                        <| Dict.keys f.allRegions )
            ]
          , tr []
            [ td [class "filtertitle"] [text "Filter by organization:"]
            , td [] <| ( List.map (btn f Organization)
                        <| List.sort
                        <| Dict.keys f.allOrgs )
            ]
          ]
        ]
      , div
          [id "filternewsletter"]
          [ button [] [text "Save filters to daily newsletter"]]
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
  in
    table [id "jobtable", class "shadow"]
      (
        [ tr []
          [ th [onClick address (SortJobs Organization), class "leftHead"] [text "Organization"]
          , th [onClick address (SortJobs Title), class "leftHead"] [text "Title"]
          , th [onClick address (SortJobs Salary), class "rightHead"] [text "Salary/Wage"]
          , th [onClick address (SortJobs ClosingDate), class "rightHead"] [text "Closing Date"]
          ]
        ]
        ++ tbody
      )

individualJob : (Bool, Job) -> List Html
individualJob (shaded, job) =
  let

      orgAndDiv = if job.division /= "" then job.organization ++ ", " ++ job.division else job.organization
      rowClass = if shaded then "shadedRow" else "unshadedRow"
  in
  [tr [class rowClass]
    [
      td [] [text <| orgAndDiv]
    , td [] [a
              [href job.urlDetail]
              [text job.title]
            ]
    , td [align "right"] [text <| salary job.salaryAmount job.salaryWaged]
    , td [align "right"] [text job.dateClosing]
    ]
  ]

salary : Float -> Bool -> String
salary amount waged =
  let stringSalary = if waged then toString amount else addCommas amount
      postfix = if waged then " /hr" else " /yr"
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

Gainful makes government job postings simple and sane. Every day, it finds all the newest postings and present them in a table. You can filter and sort listings however you want, and save your results as a daily email newsletter.

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

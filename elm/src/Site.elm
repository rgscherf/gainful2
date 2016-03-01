module Site where

import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (..)
import Markdown

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
    , viewJobs address model.jobs
    , aboutMessage
    ]

-- NAV

navBar : Html
navBar =
  nav [class "logo"] [text "Gainful"]

-- Job table

viewJobs : Signal.Address Action -> Maybe Jobs -> Html
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

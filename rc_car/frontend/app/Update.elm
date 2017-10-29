module Update exposing (..)

import WebSocket
import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (..)

import Char exposing (fromCode)
import Json.Encode
import Json.Decode

import Model exposing (..)
import Constants exposing (echoServer)

import Debug
import Subscriptions exposing (Msg)


update : Msg -> Model -> (Model, Cmd Msg)
update msg model =
  let
    sendCommand1_str cmd arg1 =
      let
        encoded_data = (Json.Encode.encode 0
            (Json.Encode.object
              [("cmd", Json.Encode.string cmd)
              ,("arg1", Json.Encode.string arg1)
              ]))
      in
      let
        _ = Debug.log "send data" encoded_data
      in
        WebSocket.send model.flags.sys_url encoded_data
    sendCommand1 cmd arg1 =
      let
        encoded_data = (Json.Encode.encode 0
            (Json.Encode.object
              [("cmd", Json.Encode.string cmd)
              ,("arg1", Json.Encode.int arg1)
              ]))
      in
      let
        _ = Debug.log "send data" encoded_data
      in
        WebSocket.send model.flags.sys_url encoded_data
    sendCommand2 cmd arg1 arg2 =
      let
        encoded_data = (Json.Encode.encode 0
            (Json.Encode.object
              [("cmd", Json.Encode.string cmd)
              ,("arg1", Json.Encode.int arg1)
              ,("arg1", Json.Encode.int arg2)
              ]))
      in
      let
        _ = Debug.log "send data" encoded_data
      in
        WebSocket.send model.flags.sys_url encoded_data
  in
    case msg of
      Subscriptions.ButtonClick buttonName ->
        case buttonName of
          "up" -> (model, sendCommand1 "throttle" 1)
          "down" -> (model, sendCommand1 "throttle" -1)
          "left" -> (model, sendCommand1 "rudder" -2)
          "right" -> (model, sendCommand1 "rudder" 2)
          "stop" -> (model, sendCommand1 "stop" 0)
          _ -> (model, Cmd.none)
      Subscriptions.KeyMsg keyCode ->
        case Char.fromCode keyCode of
          'W' -> (model, sendCommand1 "throttle" 1)
          'S' -> (model, sendCommand1 "throttle" -1)
          'A' -> (model, sendCommand1 "rudder" -2)
          'D' -> (model, sendCommand1 "rudder" 2)
          ' ' -> (model, sendCommand1 "stop" 0)
          _ -> (model, Cmd.none)
      Subscriptions.WebsocketMsg msg ->
        -- see also
        -- https://www.brianthicks.com/post/2016/06/17/how-does-json-decode-andthen-work/
        let
          _ = Debug.log "incomming" msg
          statusDecoder = Json.Decode.at ["result"] Json.Decode.string
        in
          case
            (Json.Decode.decodeString statusDecoder msg)
          of
            Ok "ok" ->
              let
                obj1 = (Json.Decode.decodeString
                  (Json.Decode.at ["sensors"] carJsonDecoder)
                  msg)
                obj2 = (Json.Decode.decodeString
                  (Json.Decode.at ["parameters"] parametersJsonDecoder)
                  msg)
              in
              case
                (obj1, obj2)
              of
                (Ok sensors, Ok parameters) ->
                  ({model| sensors = sensors, parameters = parameters}, Cmd.none)
                error ->
                  let
                    _ = Debug.log "error decode state" error
                  in
                    (model, Cmd.none)
            error ->
              let
                _ = Debug.log "error decode status" error
              in
                (model, Cmd.none)
      Subscriptions.ChangeMode mode ->
        let
          _ = Debug.log "change mode" mode
        in

        (model, sendCommand1_str "mode" mode)
      Subscriptions.ChangeDelay delay ->
          let
            parameters = model.parameters
          in
          case String.toInt delay of
            Ok v ->
              ({model | parameters = {parameters | delay = Just v}}, sendCommand1 "delay" v)
            Err error ->
              ({model | parameters = {parameters | delay = Nothing}}, Cmd.none)
      Subscriptions.SwitchHeadlamp ->
        let
          parameters = model.parameters
        in
        case parameters.headlamp of
          On ->
            ({model | parameters = {parameters | headlamp = Off}}, sendCommand1_str "headlamp" "off")
          Off ->
            ({model | parameters = {parameters | headlamp = Off}}, sendCommand1_str "headlamp" "on")
      _ ->
        (model, Cmd.none)
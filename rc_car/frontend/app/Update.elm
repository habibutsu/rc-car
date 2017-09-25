module Update exposing (..)

import WebSocket
import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (..)

import Char exposing (fromCode)
import Json.Encode as JsonEncode
import Json.Decode as JsonDecode

import Model exposing (..)
import Constants exposing (echoServer)

import Debug
import Subscriptions exposing (Msg)




update : Msg -> Model -> (Model, Cmd Msg)
update msg model =
  let
    sendCommand cmd value =
      let
        encoded_data = (JsonEncode.encode 0
            (JsonEncode.object [
              ("cmd", JsonEncode.string cmd),
              ("value", JsonEncode.int value)]))
      in
      let
        _ = Debug.log "send data" encoded_data
      in
        WebSocket.send model.flags.sys_url encoded_data
  in
    case msg of
      Subscriptions.ButtonClick buttonName ->
        case buttonName of
          "up" -> (model, sendCommand "accelerate" 1)
          "down" -> (model, sendCommand "accelerate" -1)
          "left" -> (model, sendCommand "drive" -2)
          "right" -> (model, sendCommand "drive" 2)
          _ -> (model, Cmd.none)
      Subscriptions.KeyMsg keyCode ->
        case Char.fromCode keyCode of
          'W' -> (model, sendCommand "accelerate" 1)
          'S' -> (model, sendCommand "accelerate" -1)
          'A' -> (model, sendCommand "drive" -2)
          'D' -> (model, sendCommand "drive" 2)
          ' ' -> (model, sendCommand "stop" 0)
          _ -> (model, Cmd.none)
      Subscriptions.WebsocketMsg msg ->
        -- see also
        -- https://www.brianthicks.com/post/2016/06/17/how-does-json-decode-andthen-work/
        let
          _ = Debug.log "incomming" msg
          statusDecoder = JsonDecode.at ["result"] JsonDecode.string
        in
          case
            (JsonDecode.decodeString statusDecoder msg)
          of
            Ok "ok" ->
              case
                (JsonDecode.decodeString
                  (JsonDecode.at ["state"] carJsonDecoder)
                  msg)
              of
                Ok state ->
                  ({model| car = state}, Cmd.none)
                error ->
                  let
                    _ = Debug.log "error decode state" error
                  in
                    (model, Cmd.none)
            Ok "error" ->

              (model, Cmd.none)
            error ->
              let
                _ = Debug.log "error decode status" error
              in
                (model, Cmd.none)
      _ ->
        (model, Cmd.none)
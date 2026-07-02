import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

import 'package:nfc_manager/ndef_record.dart';
import 'package:nfc_manager/nfc_manager.dart';
import 'package:nfc_manager_ndef/nfc_manager_ndef.dart';

import 'card_reader.dart';

class NfcCardReader implements CardReader {
  static const _pollingOptions = {
    NfcPollingOption.iso14443,
    NfcPollingOption.iso15693,
    NfcPollingOption.iso18092,
  };

  static const _language = 'en';

  Completer<String>? _pendingRead;
  Completer<void>? _pendingWrite;

  @override
  Future<bool> isAvailable() async {
    final availability = await NfcManager.instance.checkAvailability();
    return availability == NfcAvailability.enabled;
  }

  @override
  Future<String> readCardId() {
    final completer = Completer<String>();
    _pendingRead = completer;
    NfcManager.instance.startSession(
      pollingOptions: _pollingOptions,
      onDiscovered: (NfcTag tag) async {
        try {
          final ndef = Ndef.from(tag);
          if (ndef == null) {
            throw const FormatException("Ce tag n'est pas au format NDEF.");
          }
          final message = await ndef.read();
          if (message == null || message.records.isEmpty) {
            throw const FormatException('Tag NFC vide.');
          }
          final id = _decodeTextPayload(message.records.first.payload);
          if (!completer.isCompleted) completer.complete(id);
        } catch (e) {
          if (!completer.isCompleted) completer.completeError(e);
        } finally {
          await NfcManager.instance.stopSession();
        }
      },
    );
    return completer.future;
  }

  @override
  Future<void> writeCardId(String id) {
    final completer = Completer<void>();
    _pendingWrite = completer;
    NfcManager.instance.startSession(
      pollingOptions: _pollingOptions,
      onDiscovered: (NfcTag tag) async {
        try {
          final ndef = Ndef.from(tag);
          if (ndef == null) {
            throw const FormatException('Ce tag ne supporte pas NDEF.');
          }
          await ndef.write(message: NdefMessage(records: [_createTextRecord(id)]));
          if (!completer.isCompleted) completer.complete();
        } catch (e) {
          if (!completer.isCompleted) completer.completeError(e);
        } finally {
          await NfcManager.instance.stopSession();
        }
      },
    );
    return completer.future;
  }

  @override
  Future<void> cancelSession() async {
    await NfcManager.instance.stopSession();
    if (_pendingRead != null && !_pendingRead!.isCompleted) {
      _pendingRead!.completeError(const FormatException('Scan annulé.'));
    }
    if (_pendingWrite != null && !_pendingWrite!.isCompleted) {
      _pendingWrite!.completeError(const FormatException('Écriture annulée.'));
    }
  }

  /// Construit un record NDEF "Text" (RTD "T") en UTF-8, langue "en".
  NdefRecord _createTextRecord(String text) {
    final languageBytes = utf8.encode(_language);
    final textBytes = utf8.encode(text);
    final payload = Uint8List.fromList([
      languageBytes.length,
      ...languageBytes,
      ...textBytes,
    ]);
    return NdefRecord(
      typeNameFormat: TypeNameFormat.wellKnown,
      type: Uint8List.fromList('T'.codeUnits),
      identifier: Uint8List(0),
      payload: payload,
    );
  }

  /// Décode un payload de record NDEF texte (statut + code langue + texte).
  /// On suppose un encodage UTF-8 : tous nos tags sont écrits par _createTextRecord,
  /// qui encode en UTF-8 par défaut.
  String _decodeTextPayload(Uint8List payload) {
    if (payload.isEmpty) {
      throw const FormatException('Tag NFC vide.');
    }
    final languageCodeLength = payload[0] & 0x3f;
    final textStart = 1 + languageCodeLength;
    if (textStart > payload.length) {
      throw const FormatException('Format de tag NFC invalide.');
    }
    return utf8.decode(payload.sublist(textStart));
  }
}

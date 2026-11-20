from pathlib import Path
root = Path(__file__).resolve().parent.parent
script_path = root / "scripts" / "main.gd"
s = script_path.read_text(encoding="utf-8")
old = '''        var expires_at_ms := int(pending_vote.get("expiresAt", 0))
        var remaining_ms := maxi(0, expires_at_ms - int(Time.get_unix_time_from_system() * 1000.0))
        var seconds_left := int(ceil(float(remaining_ms) / 1000.0))
        vote_text += "\\nДО КОНЦА ГОЛОСОВАНИЯ: %d СЕК." % seconds_left
        status_label.text = vote_text'''
new = '''        var now_ms := int(Time.get_unix_time_from_system() * 1000.0)
        var discussion_ends_ms := int(pending_vote.get("discussionEndsAt", 0))
        var expires_at_ms := int(pending_vote.get("expiresAt", 0))
        var in_discussion := now_ms < discussion_ends_ms
        var phase_end_ms := discussion_ends_ms if in_discussion else expires_at_ms
        var remaining_ms := maxi(0, phase_end_ms - now_ms)
        var seconds_left := int(ceil(float(remaining_ms) / 1000.0))
        if in_discussion:
            vote_text = "ОБСУЖДЕНИЕ ХОДА • %d СЕК." % seconds_left
        else:
            vote_text += "\\nГОЛОСОВАНИЕ: %d СЕК." % seconds_left
        status_label.text = vote_text'''
if s.count(old) != 1: raise SystemExit(f"countdown anchor {s.count(old)}")
s=s.replace(old,new,1)
old2='''        var can_vote := voting_active and not _server_viewer_eliminated and not already_voted
        vote_approve_button.visible = can_vote
        vote_reject_button.visible = can_vote'''
new2='''        var now_ms := int(Time.get_unix_time_from_system() * 1000.0)
        var discussion_ends_ms := int(pending_vote.get("discussionEndsAt", 0))
        var discussion_over := now_ms >= discussion_ends_ms
        var can_vote := voting_active and discussion_over and not _server_viewer_eliminated and not already_voted
        vote_approve_button.visible = can_vote
        vote_reject_button.visible = can_vote'''
if s.count(old2)!=1: raise SystemExit(f"button anchor {s.count(old2)}")
s=s.replace(old2,new2,1)
script_path.write_text(s,encoding="utf-8")
print("CHECKMATE v42 discussion/voting phases patch applied")

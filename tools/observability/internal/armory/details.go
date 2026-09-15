package armory

import (
	"database/sql"
	"fmt"
	"strings"
)

// detailSelect lists the tooltip columns of world.item_template appended
// after the base item columns. Order must match scanDetailRow.
const detailSelect = `it.class, it.subclass, it.description, it.bonding,
	it.required_level, it.required_skill, it.allowable_class, it.allowable_race,
	it.max_count, it.stackable, it.container_slots, it.delay, it.ammo_type,
	it.dmg_min1, it.dmg_max1, it.dmg_type1,
	it.dmg_min2, it.dmg_max2, it.dmg_min3, it.dmg_max3,
	it.block, it.armor,
	it.holy_res, it.fire_res, it.nature_res, it.frost_res, it.shadow_res, it.arcane_res,
	it.stat_type1, it.stat_value1, it.stat_type2, it.stat_value2,
	it.stat_type3, it.stat_value3, it.stat_type4, it.stat_value4,
	it.stat_type5, it.stat_value5, it.stat_type6, it.stat_value6,
	it.stat_type7, it.stat_value7, it.stat_type8, it.stat_value8,
	it.stat_type9, it.stat_value9, it.stat_type10, it.stat_value10,
	it.spellid_1, it.spelltrigger_1, it.spellid_2, it.spelltrigger_2,
	it.spellid_3, it.spelltrigger_3, it.spellid_4, it.spelltrigger_4,
	it.spellid_5, it.spelltrigger_5,
	it.max_durability, it.sell_price`

// detailDests returns scan destinations for detailSelect in order.
func detailDests(d *ItemDetail, st, sv *[10]int32, sp *[5]uint32, tr *[5]uint8) []interface{} {
	return []interface{}{
		&d.Class, &d.SubClass, &d.Description, &d.Bonding,
		&d.RequiredLevel, &d.RequiredSkill, &d.AllowableClass, &d.AllowableRace,
		&d.MaxCount, &d.Stackable, &d.ContainerSlots, &d.Delay, &d.AmmoType,
		&d.DmgMin1, &d.DmgMax1, &d.DmgType1,
		&d.DmgMin2, &d.DmgMax2, &d.DmgMin3, &d.DmgMax3,
		&d.Block, &d.Armor,
		&d.ResHoly, &d.ResFire, &d.ResNature, &d.ResFrost, &d.ResShadow, &d.ResArcane,
		&st[0], &sv[0], &st[1], &sv[1], &st[2], &sv[2], &st[3], &sv[3], &st[4], &sv[4],
		&st[5], &sv[5], &st[6], &sv[6], &st[7], &sv[7], &st[8], &sv[8], &st[9], &sv[9],
		&sp[0], &tr[0], &sp[1], &tr[1], &sp[2], &tr[2], &sp[3], &tr[3], &sp[4], &tr[4],
		&d.MaxDurability, &d.SellPrice,
	}
}

// foldDetail compacts sparse stat/spell columns into the JSON slices.
func foldDetail(d *ItemDetail, st, sv [10]int32, sp [5]uint32, tr [5]uint8) {
	for i := range st {
		if sv[i] == 0 {
			continue
		}
		d.StatTypes = append(d.StatTypes, uint8(st[i]))
		d.StatValues = append(d.StatValues, sv[i])
	}
	for i := range sp {
		if sp[i] == 0 {
			continue
		}
		d.SpellIDs = append(d.SpellIDs, sp[i])
		d.SpellTriggers = append(d.SpellTriggers, tr[i])
	}
}

// resolveSpellNames fills human-readable proc names from the operator's own
// spell_template in one query. Best effort: names are tooltip sugar, never
// fail the load.
func (s *Service) resolveSpellNames(d *ItemDetail) {
	if len(d.SpellIDs) == 0 {
		return
	}
	d.SpellNames = make([]string, len(d.SpellIDs))
	names := s.spellNames(d.SpellIDs)
	for i, sid := range d.SpellIDs {
		d.SpellNames[i] = names[sid]
	}
}
func (s *Service) spellName(spellID uint32) string {
	return s.spellNames([]uint32{spellID})[spellID]
}

// spellNames resolves many spell display names in one query.
func (s *Service) spellNames(ids []uint32) map[uint32]string {
	out := map[uint32]string{}
	seen := map[uint32]bool{}
	var args []interface{}
	var marks []string
	for _, id := range ids {
		if id == 0 || seen[id] {
			continue
		}
		seen[id] = true
		marks = append(marks, "?")
		args = append(args, id)
	}
	if len(marks) == 0 {
		return out
	}
	q := fmt.Sprintf(`SELECT entry, name FROM %s.spell_template WHERE entry IN (%s)`, s.cfg.WorldDB, strings.Join(marks, ","))
	rows, err := s.db.Query(q, args...)
	if err != nil {
		return out
	}
	defer rows.Close()
	for rows.Next() {
		var entry uint32
		var name sql.NullString
		if err := rows.Scan(&entry, &name); err != nil || !name.Valid {
			continue
		}
		out[entry] = name.String
	}
	return out
}

// firstRanks collects rank-1 spell ids of class talents for batch naming.
func firstRanks(talents []dbcTalent, tabByID map[uint32]dbcTalentTab) []uint32 {
	ids := make([]uint32, 0, len(talents))
	for _, t := range talents {
		if _, ok := tabByID[t.tabID]; !ok || len(t.ranks) == 0 {
			continue
		}
		ids = append(ids, t.ranks[0])
	}
	return ids
}

func scanDetailTail(rows *sql.Rows, d *ItemDetail, s *Service) error {
	var st, sv [10]int32
	var sp [5]uint32
	var tr [5]uint8
	if err := rows.Scan(detailDests(d, &st, &sv, &sp, &tr)...); err != nil {
		return err
	}
	foldDetail(d, st, sv, sp, tr)
	if s != nil {
		s.resolveSpellNames(d)
	}
	return nil
}

CREATE OR REPLACE VIEW public.company_rights_view
 AS
 SELECT comp.id,
    sc.id AS component_id,
    sc.component,
    sc.component_desc AS "desc",
    sc.type,
    sc.key,
    sc.parent_component AS parent,
    sc.is_active AS is_component_active,
    comp.date_added,
    comp.is_active,
    cpy.id AS company_id,
    cpy.name AS company_name,
    cpy.short_name AS company_short_name
   FROM system_component sc
     JOIN company_component comp ON comp.system_component_id = sc.id
     JOIN company cpy ON cpy.id = comp.company_id;
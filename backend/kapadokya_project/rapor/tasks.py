import json
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.utils import timezone
from celery import shared_task
import numpy as np

from .models import Report, ReportTemplate, ScheduledReport, AIAnalysis
from kapadokya_project.isg.models import SafetyViolation, SafetyReport
from kapadokya_project.verim_sistemi.models import WorkerActivity, ProductivityData, ProductionCount

@shared_task
def generate_report(template_id, start_date_str, end_date_str, user_id):
    """Generate a report based on a template"""
    try:
        # Convert string dates to datetime objects
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        # Get the template and user
        template = ReportTemplate.objects.get(id=template_id)
        user = User.objects.get(id=user_id)
        
        # Create a title for the report
        title = f"{template.name} ({start_date_str} - {end_date_str})"
        
        # Initialize the report data
        report_data = {
            'config': template.config,
            'summary': {},
            'details': {},
            'metrics': []
        }
        
        # Generate report data based on report type
        if template.report_type == 'isg':
            report_data = generate_isg_report_data(start_date, end_date, template.config, report_data)
        elif template.report_type == 'verimlilik':
            report_data = generate_productivity_report_data(start_date, end_date, template.config, report_data)
        elif template.report_type == 'uretim':
            report_data = generate_production_report_data(start_date, end_date, template.config, report_data)
        else:  # general report
            report_data = generate_general_report_data(start_date, end_date, template.config, report_data)
        
        # Generate charts configuration
        charts = generate_charts_config(template.report_type, report_data)
        
        # Create the report
        report = Report.objects.create(
            title=title,
            report_type=template.report_type,
            start_date=start_date,
            end_date=end_date,
            created_by=user,
            data=report_data,
            charts=charts,
            notes=f"Otomatik olarak '{template.name}' şablonundan oluşturuldu."
        )
        
        # Now generate AI analysis if configured
        if template.config.get('generate_ai_analysis', False):
            generate_ai_analysis.delay(report.id)
        
        return report.id
    
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        return None


def generate_isg_report_data(start_date, end_date, config, report_data):
    """Generate data for ISG (Health & Safety) reports"""
    # Convert dates to datetime for filtering
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    # Get all safety violations in date range
    violations = SafetyViolation.objects.filter(
        timestamp__range=(start_datetime, end_datetime)
    )
    
    # Get all safety reports in date range
    safety_reports = SafetyReport.objects.filter(
        report_date__range=(start_date, end_date)
    )
    
    # Calculate summary statistics
    total_violations = violations.count()
    resolved_violations = violations.filter(resolved=True).count()
    resolution_rate = (resolved_violations / total_violations * 100) if total_violations > 0 else 0
    
    violation_types = {
        'missing_equipment': violations.filter(violation_type='missing_equipment').count(),
        'danger_zone': violations.filter(violation_type='danger_zone').count(),
        'unauthorized_entry': violations.filter(violation_type='unauthorized_entry').count()
    }
    
    # Add summary to report data
    report_data['summary'] = {
        'total_violations': total_violations,
        'resolved_violations': resolved_violations,
        'resolution_rate': resolution_rate,
        'violation_types': violation_types
    }
    
    # Add daily breakdown
    daily_data = {}
    current_date = start_date
    while current_date <= end_date:
        day_start = datetime.combine(current_date, datetime.min.time())
        day_end = datetime.combine(current_date, datetime.max.time())
        
        day_violations = violations.filter(timestamp__range=(day_start, day_end))
        
        daily_data[current_date.isoformat()] = {
            'total': day_violations.count(),
            'resolved': day_violations.filter(resolved=True).count(),
            'types': {
                'missing_equipment': day_violations.filter(violation_type='missing_equipment').count(),
                'danger_zone': day_violations.filter(violation_type='danger_zone').count(),
                'unauthorized_entry': day_violations.filter(violation_type='unauthorized_entry').count()
            }
        }
        
        current_date += timedelta(days=1)
    
    report_data['details']['daily'] = daily_data
    
    # Add metrics for the report
    report_data['metrics'] = [
        {
            'name': 'Toplam İhlal',
            'value': total_violations,
            'unit': 'adet'
        },
        {
            'name': 'Çözüm Oranı',
            'value': round(resolution_rate, 2),
            'unit': '%'
        },
        {
            'name': 'Ekipman Eksikliği',
            'value': violation_types['missing_equipment'],
            'unit': 'adet'
        },
        {
            'name': 'Tehlikeli Alan İhlali',
            'value': violation_types['danger_zone'],
            'unit': 'adet'
        }
    ]
    
    return report_data


def generate_productivity_report_data(start_date, end_date, config, report_data):
    """Generate data for productivity reports"""
    # Get productivity data in date range
    productivity_data = ProductivityData.objects.filter(
        date__range=(start_date, end_date)
    )
    
    # Get worker activities in date range
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    activities = WorkerActivity.objects.filter(
        timestamp__range=(start_datetime, end_datetime)
    )
    
    # Calculate summary statistics
    total_workers = productivity_data.values('worker').distinct().count()
    avg_productivity = productivity_data.values_list('productivity_score', flat=True).aggregate('avg')['productivity_score__avg'] or 0
    
    activity_types = {
        'working': activities.filter(activity_type='working').count(),
        'idle': activities.filter(activity_type='idle').count(),
        'absent': activities.filter(activity_type='absent').count(),
        'break': activities.filter(activity_type='break').count()
    }
    
    # Add summary to report data
    report_data['summary'] = {
        'total_workers': total_workers,
        'avg_productivity': avg_productivity,
        'activity_types': activity_types
    }
    
    # Add worker breakdown
    worker_data = {}
    for prod_data in productivity_data:
        worker_id = prod_data.worker_id
        worker_name = prod_data.worker.name
        
        if worker_id not in worker_data:
            worker_data[worker_id] = {
                'name': worker_name,
                'productivity': [],
                'working_time': 0,
                'idle_time': 0,
                'avg_score': 0
            }
        
        worker_data[worker_id]['productivity'].append({
            'date': prod_data.date.isoformat(),
            'score': prod_data.productivity_score,
            'working_time': prod_data.working_time,
            'idle_time': prod_data.idle_time
        })
        
        worker_data[worker_id]['working_time'] += prod_data.working_time
        worker_data[worker_id]['idle_time'] += prod_data.idle_time
    
    # Calculate average scores for each worker
    for worker_id, data in worker_data.items():
        scores = [p['score'] for p in data['productivity']]
        data['avg_score'] = sum(scores) / len(scores) if scores else 0
    
    report_data['details']['workers'] = worker_data
    
    # Add daily breakdown
    daily_data = {}
    current_date = start_date
    while current_date <= end_date:
        day_prod_data = productivity_data.filter(date=current_date)
        
        if day_prod_data.exists():
            avg_day_score = day_prod_data.values_list('productivity_score', flat=True).aggregate('avg')['productivity_score__avg'] or 0
            
            daily_data[current_date.isoformat()] = {
                'avg_productivity': avg_day_score,
                'worker_count': day_prod_data.values('worker').distinct().count()
            }
        else:
            daily_data[current_date.isoformat()] = {
                'avg_productivity': 0,
                'worker_count': 0
            }
        
        current_date += timedelta(days=1)
    
    report_data['details']['daily'] = daily_data
    
    # Add metrics for the report
    report_data['metrics'] = [
        {
            'name': 'Ortalama Verimlilik',
            'value': round(avg_productivity, 2),
            'unit': '%'
        },
        {
            'name': 'Toplam Çalışan',
            'value': total_workers,
            'unit': 'kişi'
        },
        {
            'name': 'Aktif Çalışma Oranı',
            'value': round(activity_types['working'] / sum(activity_types.values()) * 100, 2) if sum(activity_types.values()) > 0 else 0,
            'unit': '%'
        }
    ]
    
    return report_data
def generate_production_report_data(start_date, end_date, config, report_data):
    """Generate data for production reports"""
    # Get production data in date range
    production_data = ProductionCount.objects.filter(
        date__range=(start_date, end_date)
    )
    
    # Calculate summary statistics
    total_products = production_data.values_list('count', flat=True).aggregate('sum')['count__sum'] or 0
    total_defects = production_data.values_list('defect_count', flat=True).aggregate('sum')['defect_count__sum'] or 0
    defect_rate = (total_defects / total_products * 100) if total_products > 0 else 0
    
    # Add summary to report data
    report_data['summary'] = {
        'total_products': total_products,
        'total_defects': total_defects,
        'defect_rate': defect_rate
    }
    
    # Add product breakdown
    product_data = {}
    for prod_data in production_data:
        product_id = prod_data.product_id
        product_name = prod_data.product.name
        
        if product_id not in product_data:
            product_data[product_id] = {
                'name': product_name,
                'total_count': 0,
                'total_defects': 0,
                'daily_counts': {}
            }
        
        product_data[product_id]['total_count'] += prod_data.count
        product_data[product_id]['total_defects'] += prod_data.defect_count
        
        product_data[product_id]['daily_counts'][prod_data.date.isoformat()] = {
            'count': prod_data.count,
            'defects': prod_data.defect_count
        }
    
    report_data['details']['products'] = product_data
    
    # Add daily breakdown
    daily_data = {}
    current_date = start_date
    while current_date <= end_date:
        day_prod_data = production_data.filter(date=current_date)
        
        if day_prod_data.exists():
            daily_count = day_prod_data.values_list('count', flat=True).aggregate('sum')['count__sum'] or 0
            daily_defects = day_prod_data.values_list('defect_count', flat=True).aggregate('sum')['defect_count__sum'] or 0
            
            daily_data[current_date.isoformat()] = {
                'count': daily_count,
                'defects': daily_defects,
                'product_count': day_prod_data.values('product').distinct().count()
            }
        else:
            daily_data[current_date.isoformat()] = {
                'count': 0,
                'defects': 0,
                'product_count': 0
            }
        
        current_date += timedelta(days=1)
    
    report_data['details']['daily'] = daily_data
    
    # Add metrics for the report
    report_data['metrics'] = [
        {
            'name': 'Toplam Üretim',
            'value': total_products,
            'unit': 'adet'
        },
        {
            'name': 'Hatalı Ürün',
            'value': total_defects,
            'unit': 'adet'
        },
        {
            'name': 'Hata Oranı',
            'value': round(defect_rate, 2),
            'unit': '%'
        }
    ]
    
    return report_data


def generate_general_report_data(start_date, end_date, config, report_data):
    """Generate data for general reports with multiple categories"""
    # This combines data from all report types
    report_data = generate_isg_report_data(start_date, end_date, config, report_data)
    
    productivity_report = generate_productivity_report_data(start_date, end_date, config, {
        'summary': {},
        'details': {},
        'metrics': []
    })
    
    production_report = generate_production_report_data(start_date, end_date, config, {
        'summary': {},
        'details': {},
        'metrics': []
    })
    
    # Merge summaries and details
    report_data['summary']['productivity'] = productivity_report['summary']
    report_data['summary']['production'] = production_report['summary']
    
    report_data['details']['productivity'] = productivity_report['details']
    report_data['details']['production'] = production_report['details']
    
    # Add metrics from all categories
    report_data['metrics'].extend(productivity_report['metrics'])
    report_data['metrics'].extend(production_report['metrics'])
    
    return report_data


def generate_charts_config(report_type, report_data):
    """Generate charts configuration based on report data"""
    charts = []
    
    if report_type == 'isg' or report_type == 'genel':
        # Add charts for ISG data
        if 'daily' in report_data['details']:
            # Daily violations chart
            daily_violation_data = []
            for date, data in report_data['details']['daily'].items():
                daily_violation_data.append({
                    'date': date,
                    'total': data['total'],
                    'resolved': data['resolved']
                })
            
            charts.append({
                'id': 'daily_violations',
                'type': 'line',
                'title': 'Günlük İhlal Sayıları',
                'data': daily_violation_data,
                'x_field': 'date',
                'y_fields': ['total', 'resolved'],
                'labels': ['Toplam', 'Çözümlenmiş']
            })
        
        # Violation types pie chart
        if 'violation_types' in report_data['summary']:
            violation_types_data = []
            for type_name, count in report_data['summary']['violation_types'].items():
                label = {
                    'missing_equipment': 'Ekipman Eksikliği',
                    'danger_zone': 'Tehlikeli Alan',
                    'unauthorized_entry': 'Yetkisiz Giriş'
                }.get(type_name, type_name)
                
                violation_types_data.append({
                    'type': label,
                    'count': count
                })
            
            charts.append({
                'id': 'violation_types',
                'type': 'pie',
                'title': 'İhlal Türleri Dağılımı',
                'data': violation_types_data,
                'name_field': 'type',
                'value_field': 'count'
            })
    
    if report_type == 'verimlilik' or report_type == 'genel':
        # Add charts for productivity data
        if 'daily' in report_data.get('details', {}).get('productivity', {}):
            # Daily productivity chart
            daily_productivity_data = []
            for date, data in report_data['details']['productivity']['daily'].items():
                daily_productivity_data.append({
                    'date': date,
                    'productivity': data['avg_productivity'],
                    'workers': data['worker_count']
                })
            
            charts.append({
                'id': 'daily_productivity',
                'type': 'line',
                'title': 'Günlük Verimlilik',
                'data': daily_productivity_data,
                'x_field': 'date',
                'y_fields': ['productivity'],
                'labels': ['Verimlilik (%)']
            })
        
        # Worker productivity comparison chart
        if 'workers' in report_data.get('details', {}).get('productivity', {}):
            worker_productivity_data = []
            for worker_id, data in report_data['details']['productivity']['workers'].items():
                worker_productivity_data.append({
                    'name': data['name'],
                    'score': data['avg_score']
                })
            
            # Sort by score descending
            worker_productivity_data.sort(key=lambda x: x['score'], reverse=True)
            
            charts.append({
                'id': 'worker_productivity',
                'type': 'bar',
                'title': 'Çalışan Verimlilik Karşılaştırması',
                'data': worker_productivity_data[:10],  # Top 10 workers
                'x_field': 'name',
                'y_fields': ['score'],
                'labels': ['Verimlilik Skoru']
            })
    
    if report_type == 'uretim' or report_type == 'genel':
        # Add charts for production data
        if 'daily' in report_data.get('details', {}).get('production', {}):
            # Daily production chart
            daily_production_data = []
            for date, data in report_data['details']['production']['daily'].items():
                daily_production_data.append({
                    'date': date,
                    'count': data['count'],
                    'defects': data['defects']
                })
            
            charts.append({
                'id': 'daily_production',
                'type': 'line',
                'title': 'Günlük Üretim',
                'data': daily_production_data,
                'x_field': 'date',
                'y_fields': ['count', 'defects'],
                'labels': ['Üretim', 'Hatalı']
            })
        
        # Product comparison chart
        if 'products' in report_data.get('details', {}).get('production', {}):
            product_data = []
            for product_id, data in report_data['details']['production']['products'].items():
                defect_rate = (data['total_defects'] / data['total_count'] * 100) if data['total_count'] > 0 else 0
                
                product_data.append({
                    'name': data['name'],
                    'count': data['total_count'],
                    'defect_rate': defect_rate
                })
            
            # Sort by count descending
            product_data.sort(key=lambda x: x['count'], reverse=True)
            
            charts.append({
                'id': 'product_comparison',
                'type': 'bar',
                'title': 'Ürün Karşılaştırması',
                'data': product_data[:10],  # Top 10 products
                'x_field': 'name',
                'y_fields': ['count'],
                'labels': ['Üretim Adedi']
            })
            
            charts.append({
                'id': 'defect_comparison',
                'type': 'bar',
                'title': 'Ürün Hata Oranları',
                'data': product_data[:10],  # Top 10 products
                'x_field': 'name',
                'y_fields': ['defect_rate'],
                'labels': ['Hata Oranı (%)']
            })
    
    return charts
@shared_task
def generate_ai_analysis(report_id):
    """Generate AI analysis for a report"""
    try:
        report = Report.objects.get(id=report_id)
        
        # Generate a summary analysis
        summary = generate_summary_analysis(report)
        AIAnalysis.objects.create(
            report=report,
            analysis_type='summary',
            content=summary,
            priority='medium'
        )
        
        # Generate trend analysis
        trend = generate_trend_analysis(report)
        if trend:
            AIAnalysis.objects.create(
                report=report,
                analysis_type='trend',
                content=trend,
                priority='medium'
            )
        
        # Generate anomaly detection analysis
        anomalies = detect_anomalies(report)
        if anomalies:
            AIAnalysis.objects.create(
                report=report,
                analysis_type='anomaly',
                content=anomalies,
                priority='high'
            )
        
        # Generate recommendations
        recommendations = generate_recommendations(report)
        if recommendations:
            AIAnalysis.objects.create(
                report=report,
                analysis_type='recommendation',
                content=recommendations,
                priority='low'
            )
        
        return True
    
    except Exception as e:
        print(f"Error generating AI analysis: {str(e)}")
        return False


def generate_summary_analysis(report):
    """Generate a summary analysis of the report"""
    summary = f"## {report.title} Rapor Özeti\n\n"
    
    if report.report_type == 'isg':
        data = report.data
        
        total_violations = data['summary'].get('total_violations', 0)
        resolution_rate = data['summary'].get('resolution_rate', 0)
        
        summary += f"Bu rapor, {report.start_date} ile {report.end_date} tarihleri arasındaki iş sağlığı ve güvenliği verilerini içermektedir.\n\n"
        summary += f"* **Toplam İhlal**: {total_violations} adet\n"
        summary += f"* **Çözülme Oranı**: {resolution_rate:.2f}%\n\n"
        
        if 'violation_types' in data['summary']:
            summary += "### İhlal Türleri\n\n"
            for type_name, count in data['summary']['violation_types'].items():
                label = {
                    'missing_equipment': 'Ekipman Eksikliği',
                    'danger_zone': 'Tehlikeli Alan İhlali',
                    'unauthorized_entry': 'Yetkisiz Giriş'
                }.get(type_name, type_name)
                
                summary += f"* **{label}**: {count} adet\n"
    
    elif report.report_type == 'verimlilik':
        data = report.data
        
        total_workers = data['summary'].get('total_workers', 0)
        avg_productivity = data['summary'].get('avg_productivity', 0)
        
        summary += f"Bu rapor, {report.start_date} ile {report.end_date} tarihleri arasındaki verimlilik verilerini içermektedir.\n\n"
        summary += f"* **Toplam Çalışan Sayısı**: {total_workers}\n"
        summary += f"* **Ortalama Verimlilik**: {avg_productivity:.2f}%\n\n"
        
        if 'workers' in data.get('details', {}):
            # Find top and bottom performers
            workers = []
            for worker_id, worker_data in data['details']['workers'].items():
                workers.append({
                    'name': worker_data['name'],
                    'score': worker_data['avg_score']
                })
            
            # Sort by score
            workers.sort(key=lambda x: x['score'], reverse=True)
            
            if workers:
                top_workers = workers[:3]
                bottom_workers = workers[-3:] if len(workers) >= 3 else []
                
                summary += "### En Yüksek Verimlilik\n\n"
                for worker in top_workers:
                    summary += f"* **{worker['name']}**: {worker['score']:.2f}%\n"
                
                if bottom_workers:
                    summary += "\n### En Düşük Verimlilik\n\n"
                    for worker in bottom_workers:
                        summary += f"* **{worker['name']}**: {worker['score']:.2f}%\n"
    
    elif report.report_type == 'uretim':
        data = report.data
        
        total_products = data['summary'].get('total_products', 0)
        total_defects = data['summary'].get('total_defects', 0)
        defect_rate = data['summary'].get('defect_rate', 0)
        
        summary += f"Bu rapor, {report.start_date} ile {report.end_date} tarihleri arasındaki üretim verilerini içermektedir.\n\n"
        summary += f"* **Toplam Üretim**: {total_products} adet\n"
        summary += f"* **Hatalı Ürün**: {total_defects} adet\n"
        summary += f"* **Hata Oranı**: {defect_rate:.2f}%\n\n"
        
        if 'products' in data.get('details', {}):
            # Find top products by count
            products = []
            for product_id, product_data in data['details']['products'].items():
                defect_rate = (product_data['total_defects'] / product_data['total_count'] * 100) if product_data['total_count'] > 0 else 0
                
                products.append({
                    'name': product_data['name'],
                    'count': product_data['total_count'],
                    'defect_rate': defect_rate
                })
            
            # Sort by count
            products.sort(key=lambda x: x['count'], reverse=True)
            
            if products:
                top_products = products[:3]
                
                summary += "### En Çok Üretilen Ürünler\n\n"
                for product in top_products:
                    summary += f"* **{product['name']}**: {product['count']} adet (Hata Oranı: {product['defect_rate']:.2f}%)\n"
    
    else:  # general report
        summary += f"Bu genel rapor, {report.start_date} ile {report.end_date} tarihleri arasındaki verileri içermektedir.\n\n"
        summary += "Rapor, iş sağlığı ve güvenliği, verimlilik ve üretim verilerinin bir özetini içermektedir.\n"
    
    return summary


def generate_trend_analysis(report):
    """Generate trend analysis based on the report data"""
    trends = "## Trend Analizi\n\n"
    has_trends = False
    
    if report.report_type == 'isg' or report.report_type == 'genel':
        # Analyze daily violation trends
        if 'daily' in report.data.get('details', {}):
            daily_data = report.data['details']['daily']
            dates = sorted(daily_data.keys())
            
            if len(dates) >= 3:  # At least 3 days of data
                violations = [daily_data[date]['total'] for date in dates]
                
                # Detect trend direction
                trend_direction = None
                if violations[-1] > violations[0]:
                    trend_direction = "artış"
                elif violations[-1] < violations[0]:
                    trend_direction = "azalış"
                
                if trend_direction:
                    has_trends = True
                    trends += f"* İhlal sayısında {trend_direction} trendi görülmektedir.\n"
                    
                    if trend_direction == "artış":
                        trends += "  * Bu durum, güvenlik önlemlerinin gözden geçirilmesi gerektiğini gösteriyor olabilir.\n"
                    else:
                        trends += "  * Bu durum, alınan güvenlik önlemlerinin etkili olduğunu gösteriyor olabilir.\n"
    
    if report.report_type == 'verimlilik' or report.report_type == 'genel':
        # Analyze productivity trends
        if 'daily' in report.data.get('details', {}).get('productivity', {}):
            daily_data = report.data['details']['productivity']['daily']
            dates = sorted(daily_data.keys())
            
            if len(dates) >= 3:  # At least 3 days of data
                productivity = [daily_data[date]['avg_productivity'] for date in dates]
                
                # Detect trend direction
                trend_direction = None
                if productivity[-1] > productivity[0]:
                    trend_direction = "artış"
                elif productivity[-1] < productivity[0]:
                    trend_direction = "azalış"
                
                if trend_direction:
                    has_trends = True
                    trends += f"* Verimlilik skorunda {trend_direction} trendi görülmektedir.\n"
                    
                    if trend_direction == "artış":
                        trends += "  * Bu durum, işyeri verimliliğinin iyileştiğini gösteriyor olabilir.\n"
                    else:
                        trends += "  * Bu durum, verimlilik sorunlarına işaret ediyor olabilir.\n"
    
    if report.report_type == 'uretim' or report.report_type == 'genel':
        # Analyze production trends
        if 'daily' in report.data.get('details', {}).get('production', {}):
            daily_data = report.data['details']['production']['daily']
            dates = sorted(daily_data.keys())
            
            if len(dates) >= 3:  # At least 3 days of data
                production = [daily_data[date]['count'] for date in dates]
                defects = [daily_data[date]['defects'] for date in dates]
                
                # Detect production trend
                prod_trend = None
                if production[-1] > production[0]:
                    prod_trend = "artış"
                elif production[-1] < production[0]:
                    prod_trend = "azalış"
                
                # Detect defect trend
                defect_trend = None
                if defects[-1] > defects[0]:
                    defect_trend = "artış"
                elif defects[-1] < defects[0]:
                    defect_trend = "azalış"
                
                if prod_trend:
                    has_trends = True
                    trends += f"* Üretim miktarında {prod_trend} trendi görülmektedir.\n"
                
                if defect_trend:
                    has_trends = True
                    trends += f"* Hatalı ürün sayısında {defect_trend} trendi görülmektedir.\n"
                    
                    if defect_trend == "artış":
                        trends += "  * Bu durum, kalite kontrol süreçlerinin gözden geçirilmesi gerektiğini gösteriyor olabilir.\n"
                    else:
                        trends += "  * Bu durum, kalite iyileştirme çalışmalarının etkili olduğunu gösteriyor olabilir.\n"
    
    return trends if has_trends else None


def detect_anomalies(report):
    """Detect anomalies in the report data"""
    anomalies = "## Anomali Tespiti\n\n"
    has_anomalies = False
    
    if report.report_type == 'isg' or report.report_type == 'genel':
        if 'daily' in report.data.get('details', {}):
            daily_data = report.data['details']['daily']
            dates = sorted(daily_data.keys())
            
            if len(dates) >= 5:  # Need enough data for anomaly detection
                violations = [daily_data[date]['total'] for date in dates]
                
                # Calculate mean and standard deviation
                mean = sum(violations) / len(violations)
                std_dev = (sum((x - mean) ** 2 for x in violations) / len(violations)) ** 0.5
                
                # Detect outliers (more than 2 standard deviations from the mean)
                threshold = 2 * std_dev
                
                for i, date in enumerate(dates):
                    if abs(violations[i] - mean) > threshold:
                        has_anomalies = True
                        direction = "yüksek" if violations[i] > mean else "düşük"
                        anomalies += f"* **{date}** tarihinde {violations[i]} ihlal tespit edildi - ortalamadan anormal derecede {direction}.\n"
    
    if report.report_type == 'verimlilik' or report.report_type == 'genel':
        if 'daily' in report.data.get('details', {}).get('productivity', {}):
            daily_data = report.data['details']['productivity']['daily']
            dates = sorted(daily_data.keys())
            
            if len(dates) >= 5:
                productivity = [daily_data[date]['avg_productivity'] for date in dates]
                
                # Calculate mean and standard deviation
                mean = sum(productivity) / len(productivity)
                std_dev = (sum((x - mean) ** 2 for x in productivity) / len(productivity)) ** 0.5
                
                # Detect outliers
                threshold = 2 * std_dev
                
                for i, date in enumerate(dates):
                    if abs(productivity[i] - mean) > threshold:
                        has_anomalies = True
                        direction = "yüksek" if productivity[i] > mean else "düşük"
                        anomalies += f"* **{date}** tarihinde %{productivity[i]:.2f} verimlilik skoru - ortalamadan anormal derecede {direction}.\n"
        
        # Check for workers with unusually low productivity
        if 'workers' in report.data.get('details', {}).get('productivity', {}):
            worker_data = report.data['details']['productivity']['workers']
            scores = [data['avg_score'] for data in worker_data.values()]
            
            if scores:
                mean = sum(scores) / len(scores)
                std_dev = (sum((x - mean) ** 2 for x in scores) / len(scores)) ** 0.5
                
                # Detect workers with unusually low productivity
                threshold = 1.5 * std_dev
                
                low_performers = []
                for worker_id, data in worker_data.items():
                    if mean - data['avg_score'] > threshold:
                        low_performers.append((data['name'], data['avg_score']))
                
                if low_performers:
                    has_anomalies = True
                    anomalies += "\n### Anormal Düşük Verimlilik Gösteren Çalışanlar\n\n"
                    for name, score in low_performers:
                        anomalies += f"* **{name}**: %{score:.2f} verimlilik (ortalama: %{mean:.2f})\n"
    
    if report.report_type == 'uretim' or report.report_type == 'genel':
        if 'daily' in report.data.get('details', {}).get('production', {}):
            daily_data = report.data['details']['production']['daily']
            dates = sorted(daily_data.keys())
            
            if len(dates) >= 5:
                defect_rates = []
                for date in dates:
                    count = daily_data[date]['count']
                    defects = daily_data[date]['defects']
                    defect_rate = (defects / count * 100) if count > 0 else 0
                    defect_rates.append((date, defect_rate))
                
                # Calculate mean and standard deviation of defect rates
                rates = [rate for _, rate in defect_rates]
                if rates:
                    mean = sum(rates) / len(rates)
                    std_dev = (sum((x - mean) ** 2 for x in rates) / len(rates)) ** 0.5
                    
                    # Detect outliers
                    threshold = 2 * std_dev
                    
                    for date, rate in defect_rates:
                        if rate - mean > threshold:  # Only flag unusually high defect rates
                            has_anomalies = True
                            anomalies += f"* **{date}** tarihinde %{rate:.2f} hata oranı - ortalamadan anormal derecede yüksek.\n"
        
        # Check for products with unusually high defect rates
        if 'products' in report.data.get('details', {}).get('production', {}):
            product_data = report.data['details']['production']['products']
            
            defect_rates = []
            for product_id, data in product_data.items():
                count = data['total_count']
                defects = data['total_defects']
                if count > 0:  # Avoid division by zero
                    defect_rate = defects / count * 100
                    defect_rates.append((data['name'], defect_rate))
            
            if defect_rates:
                mean = sum(rate for _, rate in defect_rates) / len(defect_rates)
                std_dev = (sum((rate - mean) ** 2 for _, rate in defect_rates) / len(defect_rates)) ** 0.5
                
                # Detect products with unusually high defect rates
                threshold = 1.5 * std_dev
                
                problem_products = []
                for name, rate in defect_rates:
                    if rate - mean > threshold:
                        problem_products.append((name, rate))
                
                if problem_products:
                    has_anomalies = True
                    anomalies += "\n### Anormal Yüksek Hata Oranı Gösteren Ürünler\n\n"
                    for name, rate in problem_products:
                        anomalies += f"* **{name}**: %{rate:.2f} hata oranı (ortalama: %{mean:.2f})\n"
    
    return anomalies if has_anomalies else None


def generate_recommendations(report):
    """Generate recommendations based on the report data"""
    recommendations = "## Öneriler ve Aksiyon Planı\n\n"
    has_recommendations = False
    
    if report.report_type == 'isg' or report.report_type == 'genel':
        data = report.data
        
        if data['summary'].get('total_violations', 0) > 0:
            has_recommendations = True
            
            # Check resolution rate
            resolution_rate = data['summary'].get('resolution_rate', 0)
            if resolution_rate < 70:
                recommendations += "* **İhlal Çözümleme Sürecini İyileştirin**: Çözüm oranı düşük görünüyor (%{:.2f}). İhlallerin daha hızlı çözümlenmesi için süreçleri gözden geçirin.\n".format(resolution_rate)
            
            # Look at violation types
            if 'violation_types' in data['summary']:
                violation_types = data['summary']['violation_types']
                
                # Recommendations based on most common violation type
                max_type = max(violation_types.items(), key=lambda x: x[1])
                
                if max_type[0] == 'missing_equipment':
                    recommendations += "* **Güvenlik Ekipmanı Kontrollerini Artırın**: En yaygın ihlal türü ekipman eksikliği. Çalışma alanı girişlerinde kontrol noktaları oluşturun ve düzenli denetimler yapın.\n"
                    recommendations += "* **Ekipman Erişilebilirliğini İyileştirin**: Gerekli güvenlik ekipmanlarının kolayca erişilebilir olduğundan emin olun.\n"
                
                elif max_type[0] == 'danger_zone':
                    recommendations += "* **Tehlikeli Alan İşaretlemelerini Güçlendirin**: En yaygın ihlal türü tehlikeli alan ihlali. İşaretlemeleri daha görünür hale getirin ve ek bariyerler ekleyin.\n"
                    recommendations += "* **Tehlikeli Alan Eğitimlerini Artırın**: Çalışanlara tehlikeli alanların riskleri hakkında ek eğitimler verin.\n"
                
                elif max_type[0] == 'unauthorized_entry':
                    recommendations += "* **Erişim Kontrol Sistemlerini Güçlendirin**: En yaygın ihlal türü yetkisiz giriş. Erişim kontrol mekanizmalarını gözden geçirin ve gerekirse güncelleyin.\n"
    
    if report.report_type == 'verimlilik' or report.report_type == 'genel':
        data = report.data
        
        # Check overall productivity
        if 'avg_productivity' in data.get('summary', {}):
            avg_productivity = data['summary']['avg_productivity']
            
            if avg_productivity < 70:
                has_recommendations = True
                recommendations += "* **Genel Verimlilik İyileştirme Programı Başlatın**: Ortalama verimlilik skoru düşük (%{:.2f}). Verimlilik iyileştirme programları uygulamayı değerlendirin.\n".format(avg_productivity)
        
        # Check worker productivity variations
        if 'workers' in data.get('details', {}).get('productivity', {}):
            worker_data = data['details']['productivity']['workers']
            scores = [(worker_id, data['name'], data['avg_score']) for worker_id, data in worker_data.items()]
            
            # Sort by score
            scores.sort(key=lambda x: x[2])
            
            if len(scores) >= 5:
                has_recommendations = True
                bottom_performers = scores[:3]  # Bottom 3 performers
                
                recommendations += "* **Düşük Performans Gösteren Çalışanlar İçin Destek Programı Oluşturun**: Aşağıdaki çalışanlar için ek eğitim ve destek sağlayın:\n"
                for _, name, score in bottom_performers:
                    recommendations += f"  * {name} (Verimlilik: %{score:.2f})\n"
    
    if report.report_type == 'uretim' or report.report_type == 'genel':
        data = report.data
        
        # Check defect rate
        if 'defect_rate' in data.get('summary', {}):
            defect_rate = data['summary']['defect_rate']
            
            if defect_rate > 5:  # Assuming 5% is a reasonable threshold
                has_recommendations = True
                recommendations += "* **Kalite İyileştirme Programı Başlatın**: Genel hata oranı yüksek (%{:.2f}). Üretim süreçlerinde kalite kontrolü artırın.\n".format(defect_rate)
        
        # Check products with high defect rates
        if 'products' in data.get('details', {}).get('production', {}):
            product_data = data['details']['production']['products']
            
            problem_products = []
            for product_id, prod_data in product_data.items():
                if prod_data['total_count'] > 0:
                    defect_rate = prod_data['total_defects'] / prod_data['total_count'] * 100
                    if defect_rate > 8:  # Higher threshold for individual products
                        problem_products.append((prod_data['name'], defect_rate))
            
            if problem_products:
                has_recommendations = True
                recommendations += "* **Yüksek Hata Oranı Gösteren Ürünlerin Üretim Süreçlerini Gözden Geçirin**: Aşağıdaki ürünler için üretim süreçlerini optimize edin:\n"
                for name, rate in problem_products:
                    recommendations += f"  * {name} (Hata Oranı: %{rate:.2f})\n"
    
    # General recommendations that apply to all report types
    has_recommendations = True
    recommendations += "\n### Genel Öneriler\n\n"
    recommendations += "* **Düzenli Raporlama**: Verilerin daha sık ve düzenli olarak analiz edilmesi, sorunların erken tespit edilmesine yardımcı olabilir.\n"
    recommendations += "* **Çalışan Geri Bildirimleri**: Çalışanlardan düzenli geri bildirim toplayarak süreçleri iyileştirin.\n"
    recommendations += "* **YOLOv11 Modelinin Optimizasyonu**: Görüntü işleme modellerinin düzenli olarak kalibre edilmesi ve eğitilmesi, daha doğru sonuçlar elde etmenizi sağlayacaktır.\n"
    
    return recommendations if has_recommendations else None


@shared_task
def check_scheduled_reports():
    """Check for scheduled reports that need to be generated"""
    now = timezone.now()
    
    # Find schedules that are due
    schedules = ScheduledReport.objects.filter(
        is_active=True,
        next_run__lte=now
    )
    
    for schedule in schedules:
        # Generate the report
        start_date, end_date = calculate_date_range(schedule.frequency, now)
        
        try:
            # Generate the report using the template
            generate_report.delay(
                schedule.template_id,
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d'),
                schedule.template.created_by_id
            )
            
            # Calculate the next run time
            next_run = calculate_next_run(schedule, now)
            
            # Update the schedule
            schedule.last_run = now
            schedule.next_run = next_run
            schedule.save()
            
            print(f"Generated scheduled report {schedule.name}, next run at {next_run}")
        
        except Exception as e:
            print(f"Error generating scheduled report {schedule.id}: {str(e)}")
    
    return len(schedules)


def calculate_date_range(frequency, now):
    """Calculate the start and end dates for a report based on frequency"""
    end_date = now.date()
    
    if frequency == 'daily':
        # Report covers previous day
        start_date = end_date - timedelta(days=1)
    
    elif frequency == 'weekly':
        # Report covers previous week
        start_date = end_date - timedelta(days=7)
    
    elif frequency == 'monthly':
        # Report covers previous month
        if end_date.month == 1:
            start_date = end_date.replace(year=end_date.year - 1, month=12, day=1)
        else:
            start_date = end_date.replace(month=end_date.month - 1, day=1)
    
    elif frequency == 'quarterly':
        # Report covers previous quarter (3 months)
        start_date = end_date - timedelta(days=90)
    
    else:
        # Default to previous day
        start_date = end_date - timedelta(days=1)
    
    return start_date, end_date


def calculate_next_run(schedule, now):
    """Calculate the next run time for a scheduled report"""
    current_time = now.time()
    scheduled_time = schedule.time_of_day
    
    if schedule.frequency == 'daily':
        # Next day at scheduled time
        next_run = datetime.combine(now.date() + timedelta(days=1), scheduled_time)
    
    elif schedule.frequency == 'weekly':
        # Next week on the scheduled day at scheduled time
        days_ahead = schedule.day_of_week - now.weekday()
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        next_run = datetime.combine(now.date() + timedelta(days=days_ahead), scheduled_time)
    
    elif schedule.frequency == 'monthly':
        # Next month on the scheduled day at scheduled time
        year = now.year
        month = now.month + 1
        if month > 12:
            month = 1
            year += 1
        
        day = min(schedule.day_of_month or 1, [31, 29 if year % 4 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
        next_run = datetime.combine(datetime(year, month, day).date(), scheduled_time)
    
    elif schedule.frequency == 'quarterly':
        # Next quarter (3 months) on the scheduled day at scheduled time
        year = now.year
        month = now.month + 3
        if month > 12:
            month = month - 12
            year += 1
        
        day = min(schedule.day_of_month or 1, [31, 29 if year % 4 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
        next_run = datetime.combine(datetime(year, month, day).date(), scheduled_time)
    
    else:
        # Default to tomorrow at scheduled time
        next_run = datetime.combine(now.date() + timedelta(days=1), scheduled_time)
    
    return next_run

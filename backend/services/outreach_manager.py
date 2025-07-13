"""
Outreach Campaign Manager for Elite JobHunter X
Manages recruiter outreach campaigns, scheduling, and tracking
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from models import (
    OutreachCampaign, OutreachMessage, OutreachStatus, OutreachChannel,
    CampaignStatus, Recruiter, OutreachTone, OutreachTemplate, OutreachResponse
)
from services.linkedin_automation import LinkedInAutomation, LinkedInMessageGenerator
from services.gmail import GmailService
from services.openrouter import OpenRouterService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class OutreachResult:
    """Result of an outreach attempt"""
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    status: OutreachStatus = OutreachStatus.PENDING


class OutreachCampaignManager:
    """
    Manages outreach campaigns across multiple channels
    """
    
    def __init__(self, db_client):
        self.db_client = db_client
        self.db = db_client.outreach_campaigns
        self.openrouter = OpenRouterService()
        self.gmail = GmailService()
        self.linkedin_message_generator = LinkedInMessageGenerator(self.openrouter)
        
    async def create_campaign(self, candidate_id: str, campaign_data: Dict[str, Any]) -> str:
        """
        Create a new outreach campaign
        """
        try:
            campaign = OutreachCampaign(
                candidate_id=candidate_id,
                **campaign_data
            )
            
            # Insert campaign into database
            result = await self.db.campaigns.insert_one(campaign.dict())
            campaign_id = str(result.inserted_id)
            
            # Update campaign with generated ID
            await self.db.campaigns.update_one(
                {"_id": result.inserted_id},
                {"$set": {"id": campaign_id}}
            )
            
            logger.info(f"Created campaign: {campaign_id} for candidate: {candidate_id}")
            return campaign_id
            
        except Exception as e:
            logger.error(f"Error creating campaign: {str(e)}")
            raise
    
    async def start_campaign(self, campaign_id: str) -> bool:
        """
        Start an outreach campaign
        """
        try:
            # Get campaign data
            campaign = await self.db.campaigns.find_one({"id": campaign_id})
            if not campaign:
                logger.error(f"Campaign not found: {campaign_id}")
                return False
            
            # Update campaign status
            await self.db.campaigns.update_one(
                {"id": campaign_id},
                {"$set": {
                    "status": CampaignStatus.ACTIVE.value,
                    "start_date": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }}
            )
            
            # Find target recruiters
            recruiters = await self.find_target_recruiters(campaign)
            
            # Schedule outreach messages
            await self.schedule_outreach_messages(campaign, recruiters)
            
            logger.info(f"Started campaign: {campaign_id} with {len(recruiters)} recruiters")
            return True
            
        except Exception as e:
            logger.error(f"Error starting campaign: {str(e)}")
            return False
    
    async def find_target_recruiters(self, campaign: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Find recruiters matching campaign criteria
        """
        try:
            # Build search criteria
            search_criteria = {}
            
            if campaign.get('target_companies'):
                search_criteria['company'] = {"$in": campaign['target_companies']}
            
            if campaign.get('target_locations'):
                search_criteria['location'] = {"$in": campaign['target_locations']}
            
            if campaign.get('target_roles'):
                search_criteria['specializations'] = {"$in": campaign['target_roles']}
            
            search_criteria['is_active'] = True
            
            # Find recruiters
            recruiters = await self.db.recruiters.find(search_criteria).to_list(length=100)
            
            # Filter by response rate and last contact
            filtered_recruiters = []
            for recruiter in recruiters:
                # Skip if contacted recently
                if recruiter.get('last_contacted'):
                    last_contact = recruiter['last_contacted']
                    if isinstance(last_contact, str):
                        last_contact = datetime.fromisoformat(last_contact)
                    if (datetime.utcnow() - last_contact).days < 30:
                        continue
                
                # Prefer recruiters with higher response rates
                response_rate = recruiter.get('response_rate', 0.5)
                if response_rate >= 0.3:  # Minimum 30% response rate
                    filtered_recruiters.append(recruiter)
            
            # Sort by response rate descending
            filtered_recruiters.sort(key=lambda x: x.get('response_rate', 0.5), reverse=True)
            
            return filtered_recruiters
            
        except Exception as e:
            logger.error(f"Error finding target recruiters: {str(e)}")
            return []
    
    async def schedule_outreach_messages(self, campaign: Dict[str, Any], 
                                       recruiters: List[Dict[str, Any]]) -> None:
        """
        Schedule outreach messages for campaign
        """
        try:
            candidate_id = campaign['candidate_id']
            campaign_id = campaign['id']
            channels = campaign.get('channels', [OutreachChannel.LINKEDIN.value])
            daily_limit = campaign.get('daily_limit', 10)
            delay_between_messages = campaign.get('delay_between_messages', 300)
            
            # Get candidate data
            candidate = await self.db.candidates.find_one({"id": candidate_id})
            if not candidate:
                logger.error(f"Candidate not found: {candidate_id}")
                return
            
            messages_scheduled = 0
            current_date = datetime.utcnow()
            
            for recruiter in recruiters:
                if messages_scheduled >= daily_limit:
                    # Move to next day
                    current_date += timedelta(days=1)
                    messages_scheduled = 0
                
                # Schedule message for each channel
                for channel in channels:
                    # Generate personalized message
                    message_content = await self.generate_personalized_message(
                        recruiter, candidate, campaign, channel
                    )
                    
                    # Calculate scheduled time
                    scheduled_time = current_date + timedelta(
                        seconds=messages_scheduled * delay_between_messages
                    )
                    
                    # Create message record
                    message = OutreachMessage(
                        campaign_id=campaign_id,
                        recruiter_id=recruiter['id'],
                        candidate_id=candidate_id,
                        channel=OutreachChannel(channel),
                        content=message_content,
                        tone=OutreachTone(campaign.get('tone', 'warm')),
                        scheduled_for=scheduled_time,
                        status=OutreachStatus.PENDING
                    )
                    
                    await self.db.messages.insert_one(message.dict())
                    messages_scheduled += 1
                    
                    logger.info(f"Scheduled {channel} message to {recruiter['name']} for {scheduled_time}")
            
        except Exception as e:
            logger.error(f"Error scheduling outreach messages: {str(e)}")
    
    async def generate_personalized_message(self, recruiter: Dict[str, Any], 
                                          candidate: Dict[str, Any],
                                          campaign: Dict[str, Any],
                                          channel: str) -> str:
        """
        Generate personalized message for recruiter
        """
        try:
            tone = OutreachTone(campaign.get('tone', 'warm'))
            
            if channel == OutreachChannel.LINKEDIN.value:
                return await self.linkedin_message_generator.generate_outreach_message(
                    recruiter_data=recruiter,
                    candidate_data=candidate,
                    tone=tone
                )
            elif channel == OutreachChannel.EMAIL.value:
                return await self.generate_email_message(recruiter, candidate, tone)
            else:
                return self.get_generic_message(recruiter, candidate, tone)
                
        except Exception as e:
            logger.error(f"Error generating personalized message: {str(e)}")
            return self.get_fallback_message(recruiter, candidate)
    
    async def generate_email_message(self, recruiter: Dict[str, Any], 
                                   candidate: Dict[str, Any],
                                   tone: OutreachTone) -> str:
        """
        Generate email message content
        """
        try:
            prompt = f"""
            Generate a professional email for recruiter outreach:
            
            Recruiter: {recruiter.get('name', 'there')} ({recruiter.get('title', '')} at {recruiter.get('company', '')})
            Candidate: {candidate.get('full_name', '')} ({candidate.get('years_experience', 'several')} years experience)
            Skills: {', '.join(candidate.get('skills', [])[:5])}
            Target Roles: {', '.join(candidate.get('target_roles', [])[:3])}
            Tone: {tone.value}
            
            Requirements:
            - Professional email format with subject line
            - Keep body under 200 words
            - Include specific skills/experience
            - Clear call to action
            - Match the {tone.value} tone
            
            Format as:
            Subject: [subject line]
            
            [email body]
            """
            
            response = await self.openrouter.generate_completion(
                prompt=prompt,
                model="anthropic/claude-3-haiku-20240307",
                max_tokens=300
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating email message: {str(e)}")
            return self.get_fallback_email(recruiter, candidate, tone)
    
    def get_generic_message(self, recruiter: Dict[str, Any], 
                           candidate: Dict[str, Any], 
                           tone: OutreachTone) -> str:
        """
        Get generic message for unsupported channels
        """
        name = recruiter.get('name', 'there')
        
        if tone == OutreachTone.WARM:
            return f"Hi {name}, I'm {candidate.get('full_name', 'a professional')} with {candidate.get('years_experience', 'several')} years of experience. I'd love to connect and discuss potential opportunities."
        elif tone == OutreachTone.FORMAL:
            return f"Dear {name}, I am reaching out to connect regarding potential opportunities in my field. I have {candidate.get('years_experience', 'several')} years of experience and would appreciate the chance to discuss how I might contribute to your organization."
        else:
            return f"Hi {name}, I noticed your role at {recruiter.get('company', 'your company')} and would love to connect about potential opportunities."
    
    def get_fallback_message(self, recruiter: Dict[str, Any], candidate: Dict[str, Any]) -> str:
        """
        Get fallback message if generation fails
        """
        name = recruiter.get('name', 'there')
        return f"Hi {name}, I'm {candidate.get('full_name', 'a professional')} and would love to connect about potential opportunities. Thanks!"
    
    def get_fallback_email(self, recruiter: Dict[str, Any], 
                          candidate: Dict[str, Any], 
                          tone: OutreachTone) -> str:
        """
        Get fallback email if generation fails
        """
        name = recruiter.get('name', 'there')
        subject = f"Exploring opportunities - {candidate.get('full_name', 'Professional')}"
        
        body = f"""Hi {name},

I hope this email finds you well. I'm {candidate.get('full_name', 'a professional')} with {candidate.get('years_experience', 'several')} years of experience in {', '.join(candidate.get('skills', ['technology'])[:3])}.

I'm currently exploring new opportunities and would love to connect to discuss potential roles that might be a good fit.

Would you be open to a brief conversation?

Best regards,
{candidate.get('full_name', 'Professional')}"""
        
        return f"Subject: {subject}\n\n{body}"
    
    async def process_scheduled_messages(self) -> None:
        """
        Process scheduled outreach messages
        """
        try:
            # Get messages scheduled for now or earlier
            current_time = datetime.utcnow()
            
            scheduled_messages = await self.db.messages.find({
                "status": OutreachStatus.PENDING.value,
                "scheduled_for": {"$lte": current_time}
            }).to_list(length=100)
            
            logger.info(f"Processing {len(scheduled_messages)} scheduled messages")
            
            for message in scheduled_messages:
                try:
                    result = await self.send_outreach_message(message)
                    
                    # Update message status
                    update_data = {
                        "status": result.status.value,
                        "sent_at": datetime.utcnow() if result.success else None,
                        "updated_at": datetime.utcnow()
                    }
                    
                    if result.error:
                        update_data["error_message"] = result.error
                    
                    if result.message_id:
                        if message['channel'] == OutreachChannel.LINKEDIN.value:
                            update_data["linkedin_message_id"] = result.message_id
                        elif message['channel'] == OutreachChannel.EMAIL.value:
                            update_data["email_message_id"] = result.message_id
                    
                    await self.db.messages.update_one(
                        {"id": message['id']},
                        {"$set": update_data}
                    )
                    
                    # Update recruiter contact stats
                    if result.success:
                        await self.update_recruiter_stats(message['recruiter_id'])
                    
                except Exception as e:
                    logger.error(f"Error processing message {message['id']}: {str(e)}")
                    
                    # Mark as failed
                    await self.db.messages.update_one(
                        {"id": message['id']},
                        {"$set": {
                            "status": OutreachStatus.FAILED.value,
                            "error_message": str(e),
                            "updated_at": datetime.utcnow()
                        }}
                    )
                
                # Small delay between messages
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Error processing scheduled messages: {str(e)}")
    
    async def send_outreach_message(self, message: Dict[str, Any]) -> OutreachResult:
        """
        Send individual outreach message
        """
        try:
            channel = message['channel']
            candidate_id = message['candidate_id']
            recruiter_id = message['recruiter_id']
            content = message['content']
            
            if channel == OutreachChannel.LINKEDIN.value:
                return await self.send_linkedin_message(candidate_id, recruiter_id, content)
            elif channel == OutreachChannel.EMAIL.value:
                return await self.send_email_message(candidate_id, recruiter_id, content)
            else:
                return OutreachResult(
                    success=False,
                    error=f"Unsupported channel: {channel}",
                    status=OutreachStatus.FAILED
                )
                
        except Exception as e:
            logger.error(f"Error sending outreach message: {str(e)}")
            return OutreachResult(
                success=False,
                error=str(e),
                status=OutreachStatus.FAILED
            )
    
    async def send_linkedin_message(self, candidate_id: str, recruiter_id: str, 
                                   content: str) -> OutreachResult:
        """
        Send LinkedIn message
        """
        try:
            async with LinkedInAutomation(self.db_client) as linkedin:
                success = await linkedin.send_message(candidate_id, recruiter_id, content)
                
                if success:
                    return OutreachResult(
                        success=True,
                        message_id=f"linkedin_{recruiter_id}_{int(datetime.utcnow().timestamp())}",
                        status=OutreachStatus.SENT
                    )
                else:
                    return OutreachResult(
                        success=False,
                        error="Failed to send LinkedIn message",
                        status=OutreachStatus.FAILED
                    )
                    
        except Exception as e:
            logger.error(f"Error sending LinkedIn message: {str(e)}")
            return OutreachResult(
                success=False,
                error=str(e),
                status=OutreachStatus.FAILED
            )
    
    async def send_email_message(self, candidate_id: str, recruiter_id: str, 
                               content: str) -> OutreachResult:
        """
        Send email message
        """
        try:
            # Get recruiter email
            recruiter = await self.db.recruiters.find_one({"id": recruiter_id})
            if not recruiter or not recruiter.get('email'):
                return OutreachResult(
                    success=False,
                    error="No email found for recruiter",
                    status=OutreachStatus.FAILED
                )
            
            # Parse subject and body from content
            lines = content.split('\n')
            subject = lines[0].replace('Subject: ', '') if lines[0].startswith('Subject: ') else "Professional Connection"
            body = '\n'.join(lines[2:]) if len(lines) > 2 else content
            
            # Send email via Gmail service
            message_id = await self.gmail.send_email(
                candidate_id=candidate_id,
                to_email=recruiter['email'],
                subject=subject,
                body=body
            )
            
            if message_id:
                return OutreachResult(
                    success=True,
                    message_id=message_id,
                    status=OutreachStatus.SENT
                )
            else:
                return OutreachResult(
                    success=False,
                    error="Failed to send email",
                    status=OutreachStatus.FAILED
                )
                
        except Exception as e:
            logger.error(f"Error sending email message: {str(e)}")
            return OutreachResult(
                success=False,
                error=str(e),
                status=OutreachStatus.FAILED
            )
    
    async def update_recruiter_stats(self, recruiter_id: str) -> None:
        """
        Update recruiter contact statistics
        """
        try:
            await self.db.recruiters.update_one(
                {"id": recruiter_id},
                {
                    "$set": {
                        "last_contacted": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    },
                    "$inc": {"total_contacts": 1}
                }
            )
        except Exception as e:
            logger.error(f"Error updating recruiter stats: {str(e)}")
    
    async def process_follow_ups(self) -> None:
        """
        Process follow-up messages for campaigns
        """
        try:
            # Get campaigns with auto follow-up enabled
            campaigns = await self.db.campaigns.find({
                "status": CampaignStatus.ACTIVE.value,
                "auto_follow_up": True
            }).to_list(length=100)
            
            for campaign in campaigns:
                await self.process_campaign_follow_ups(campaign)
                
        except Exception as e:
            logger.error(f"Error processing follow-ups: {str(e)}")
    
    async def process_campaign_follow_ups(self, campaign: Dict[str, Any]) -> None:
        """
        Process follow-ups for a specific campaign
        """
        try:
            campaign_id = campaign['id']
            follow_up_delay = campaign.get('follow_up_delay', 86400)  # 24 hours
            max_follow_ups = campaign.get('max_follow_ups', 3)
            
            # Find messages that need follow-ups
            cutoff_time = datetime.utcnow() - timedelta(seconds=follow_up_delay)
            
            messages_needing_followup = await self.db.messages.find({
                "campaign_id": campaign_id,
                "status": OutreachStatus.SENT.value,
                "sent_at": {"$lte": cutoff_time},
                "follow_up_sequence": {"$lt": max_follow_ups},
                "replied_at": None  # No response yet
            }).to_list(length=100)
            
            for message in messages_needing_followup:
                await self.create_follow_up_message(message, campaign)
                
        except Exception as e:
            logger.error(f"Error processing campaign follow-ups: {str(e)}")
    
    async def create_follow_up_message(self, original_message: Dict[str, Any], 
                                     campaign: Dict[str, Any]) -> None:
        """
        Create follow-up message
        """
        try:
            # Get candidate and recruiter data
            candidate = await self.db.candidates.find_one({"id": original_message['candidate_id']})
            recruiter = await self.db.recruiters.find_one({"id": original_message['recruiter_id']})
            
            if not candidate or not recruiter:
                logger.error("Missing candidate or recruiter data for follow-up")
                return
            
            # Generate follow-up content
            follow_up_content = await self.generate_follow_up_message(
                original_message, candidate, recruiter, campaign
            )
            
            # Create follow-up message
            follow_up_message = OutreachMessage(
                campaign_id=campaign['id'],
                recruiter_id=original_message['recruiter_id'],
                candidate_id=original_message['candidate_id'],
                channel=OutreachChannel(original_message['channel']),
                content=follow_up_content,
                tone=OutreachTone(campaign.get('tone', 'warm')),
                is_follow_up=True,
                follow_up_sequence=original_message['follow_up_sequence'] + 1,
                parent_message_id=original_message['id'],
                scheduled_for=datetime.utcnow() + timedelta(minutes=5),  # Schedule soon
                status=OutreachStatus.PENDING
            )
            
            await self.db.messages.insert_one(follow_up_message.dict())
            
            logger.info(f"Created follow-up message for {recruiter['name']}")
            
        except Exception as e:
            logger.error(f"Error creating follow-up message: {str(e)}")
    
    async def generate_follow_up_message(self, original_message: Dict[str, Any],
                                       candidate: Dict[str, Any],
                                       recruiter: Dict[str, Any],
                                       campaign: Dict[str, Any]) -> str:
        """
        Generate follow-up message content
        """
        try:
            follow_up_sequence = original_message['follow_up_sequence'] + 1
            
            prompt = f"""
            Generate a follow-up message for recruiter outreach:
            
            Original message sent {(datetime.utcnow() - original_message['sent_at']).days} days ago
            This is follow-up #{follow_up_sequence}
            
            Recruiter: {recruiter.get('name', 'there')}
            Candidate: {candidate.get('full_name', '')}
            Channel: {original_message['channel']}
            
            Requirements:
            - Brief and polite
            - Reference the original message
            - Provide additional value or information
            - Include clear next steps
            - Keep under 150 words
            
            Follow-up message:
            """
            
            response = await self.openrouter.generate_completion(
                prompt=prompt,
                model="anthropic/claude-3-haiku-20240307",
                max_tokens=200
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating follow-up message: {str(e)}")
            return self.get_fallback_follow_up(recruiter, follow_up_sequence)
    
    def get_fallback_follow_up(self, recruiter: Dict[str, Any], sequence: int) -> str:
        """
        Get fallback follow-up message
        """
        name = recruiter.get('name', 'there')
        
        if sequence == 1:
            return f"Hi {name}, I wanted to follow up on my previous message. I'm still very interested in exploring opportunities and would love to connect when you have a moment."
        elif sequence == 2:
            return f"Hi {name}, I hope you're doing well. I wanted to reach out once more to see if there might be any opportunities that align with my background. Thanks for your time!"
        else:
            return f"Hi {name}, This will be my final follow-up. If you have any opportunities in the future, I'd love to hear from you. Thanks!"
    
    async def get_campaign_analytics(self, campaign_id: str) -> Dict[str, Any]:
        """
        Get analytics for a campaign
        """
        try:
            # Get campaign data
            campaign = await self.db.campaigns.find_one({"id": campaign_id})
            if not campaign:
                return {}
            
            # Get message statistics
            messages = await self.db.messages.find({"campaign_id": campaign_id}).to_list(length=None)
            
            total_messages = len(messages)
            sent_messages = len([m for m in messages if m['status'] == OutreachStatus.SENT.value])
            delivered_messages = len([m for m in messages if m['status'] == OutreachStatus.DELIVERED.value])
            opened_messages = len([m for m in messages if m.get('opened_at')])
            clicked_messages = len([m for m in messages if m.get('clicked_at')])
            replied_messages = len([m for m in messages if m.get('replied_at')])
            
            # Calculate rates
            send_rate = (sent_messages / total_messages) * 100 if total_messages > 0 else 0
            delivery_rate = (delivered_messages / sent_messages) * 100 if sent_messages > 0 else 0
            open_rate = (opened_messages / delivered_messages) * 100 if delivered_messages > 0 else 0
            click_rate = (clicked_messages / opened_messages) * 100 if opened_messages > 0 else 0
            response_rate = (replied_messages / sent_messages) * 100 if sent_messages > 0 else 0
            
            # Channel breakdown
            channel_stats = {}
            for channel in [OutreachChannel.LINKEDIN, OutreachChannel.EMAIL]:
                channel_messages = [m for m in messages if m['channel'] == channel.value]
                channel_stats[channel.value] = {
                    'total': len(channel_messages),
                    'sent': len([m for m in channel_messages if m['status'] == OutreachStatus.SENT.value]),
                    'replies': len([m for m in channel_messages if m.get('replied_at')])
                }
            
            return {
                'campaign_id': campaign_id,
                'campaign_name': campaign['name'],
                'status': campaign['status'],
                'total_messages': total_messages,
                'sent_messages': sent_messages,
                'delivered_messages': delivered_messages,
                'opened_messages': opened_messages,
                'clicked_messages': clicked_messages,
                'replied_messages': replied_messages,
                'send_rate': round(send_rate, 2),
                'delivery_rate': round(delivery_rate, 2),
                'open_rate': round(open_rate, 2),
                'click_rate': round(click_rate, 2),
                'response_rate': round(response_rate, 2),
                'channel_stats': channel_stats,
                'created_at': campaign['created_at'],
                'updated_at': campaign['updated_at']
            }
            
        except Exception as e:
            logger.error(f"Error getting campaign analytics: {str(e)}")
            return {}
    
    async def pause_campaign(self, campaign_id: str) -> bool:
        """
        Pause an active campaign
        """
        try:
            result = await self.db.campaigns.update_one(
                {"id": campaign_id},
                {"$set": {
                    "status": CampaignStatus.PAUSED.value,
                    "updated_at": datetime.utcnow()
                }}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error pausing campaign: {str(e)}")
            return False
    
    async def resume_campaign(self, campaign_id: str) -> bool:
        """
        Resume a paused campaign
        """
        try:
            result = await self.db.campaigns.update_one(
                {"id": campaign_id},
                {"$set": {
                    "status": CampaignStatus.ACTIVE.value,
                    "updated_at": datetime.utcnow()
                }}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error resuming campaign: {str(e)}")
            return False
    
    async def stop_campaign(self, campaign_id: str) -> bool:
        """
        Stop a campaign
        """
        try:
            result = await self.db.campaigns.update_one(
                {"id": campaign_id},
                {"$set": {
                    "status": CampaignStatus.CANCELLED.value,
                    "end_date": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error stopping campaign: {str(e)}")
            return False